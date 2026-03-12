import logging
from typing import List, Dict
from .config import config
from .utils import estimate_prob, kelly_fraction
from .fetchers import fetch_historical_data, fetch_x_sentiment
import numpy as np
import torch
from torch.autograd import Variable
from sklearn.preprocessing import MinMaxScaler
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from scipy.optimize import minimize

logger = logging.getLogger(__name__)
sia = SentimentIntensityAnalyzer()

class LSTMProb(torch.nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=100, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size)
        self.linear = nn.Linear(hidden_layer_size, output_size)
        self.hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
                            torch.zeros(1,1,self.hidden_layer_size))

    def forward(self, input_seq):
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq) ,1, -1), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]

def train_lstm(historical_prices):
    if len(historical_prices) < 2:
        return None, None
    scaler = MinMaxScaler(feature_range=(-1, 1))
    prices = scaler.fit_transform(np.array(historical_prices).reshape(-1,1))
    model = LSTMProb()
    loss_function = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    epochs = 50
    for i in range(epochs):
        for seq in range(len(prices) - 1):
            seq_data = torch.FloatTensor(prices[seq:seq+1])
            target = torch.FloatTensor(prices[seq+1:seq+2])
            model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                                 torch.zeros(1, 1, model.hidden_layer_size))
            y_pred = model(seq_data)
            single_loss = loss_function(y_pred, target)
            optimizer.zero_grad()
            single_loss.backward()
            optimizer.step()
    return model, scaler

def igarch_loglikelihood(params, returns):
    omega, alpha = params
    beta = 1 - alpha
    n = len(returns)
    sigma2 = np.zeros(n)
    epsilon = 1e-6
    sigma2[0] = np.var(returns) + epsilon
    for t in range(1, n):
        sigma2[t] = omega + alpha * returns[t-1]**2 + beta * sigma2[t-1]
    logl = -0.5 * (np.sum(np.log(2 * np.pi * sigma2[1:]) + (returns[1:]**2 / sigma2[1:])))
    return -logl

def fit_igarch(returns, initial_params=[0.01, 0.1]):
    bounds = [(-np.inf, np.inf), (0, 1)]
    res = minimize(igarch_loglikelihood, initial_params, args=(returns,), method='L-BFGS-B', bounds=bounds)
    return res.x if res.success else initial_params

def igarch_vol(returns, params):
    if len(returns) < 2:
        return 0.0
    omega, alpha = params
    beta = 1 - alpha
    n = len(returns)
    sigma2 = np.zeros(n)
    epsilon = 1e-6
    sigma2[0] = np.var(returns) + epsilon
    for t in range(1, n):
        sigma2[t] = omega + alpha * returns[t-1]**2 + beta * sigma2[t-1]
    return np.sqrt(sigma2[-1])

def estimate_true_prob_advanced(price_change_24h: float, asset: str, historical_prices: List[float], use_sentiment=True, use_igarch=True):
    base_prob = 0.5 + (price_change_24h / 100) * 0.3
    base_prob = np.clip(base_prob, 0.1, 0.9)

    model, scaler = train_lstm(historical_prices)
    if model and scaler and len(historical_prices) > 1:
        last_seq = scaler.transform(np.array(historical_prices[-30:]).reshape(-1,1))
        model.hidden_cell = (torch.zeros(1,1,model.hidden_layer_size),
                             torch.zeros(1,1,model.hidden_layer_size))
        forecast = model(torch.FloatTensor(last_seq)).item()
        forecast_prob_adjust = (forecast + 1) / 2
        base_prob = (base_prob + forecast_prob_adjust) / 2

    if use_igarch and len(historical_prices) > 1:
        returns = np.diff(historical_prices) / historical_prices[:-1]
        params = fit_igarch(returns)
        vol = igarch_vol(returns, params)
        base_prob = 0.5 + (base_prob - 0.5) * (1 - vol)

    if use_sentiment:
        sentiment_posts = fetch_x_sentiment(asset)
        if sentiment_posts:
            scores = [sia.polarity_scores(p['content'])['compound'] for p in sentiment_posts]
            avg_sent = np.mean(scores)
            base_prob += avg_sent * 0.15

    return np.clip(base_prob, 0.1, 0.9)

def find_edges(markets: List[Dict], crypto_data: List[Dict], edge_threshold: float = None, min_liquidity: float = None, use_sentiment=True, use_igarch=True) -> List[Dict]:
    threshold = edge_threshold if edge_threshold is not None else config.edge_threshold
    liquidity_min = min_liquidity if min_liquidity is not None else config.min_liquidity

    crypto_lookup = {item["id"]: item for item in crypto_data}
    edges = []

    for market in markets:
        question = market.get("question", "").lower()
        tokens = market.get("tokens", [])
        if not tokens:
            continue

        matched_asset = None
        for asset_data in crypto_data:
            symbol = asset_data.get("symbol", "").lower()
            name = asset_data.get("name", "").lower()
            if symbol in question or name in question:
                matched_asset = asset_data
                break

        if not matched_asset:
            continue

        yes_token = next((t for t in tokens if t.get("outcome", "").lower() == "yes"), None)
        if not yes_token:
            continue

        yes_price = float(yes_token.get("price", 0))
        liquidity = float(market.get("liquidity", 0))

        if liquidity < liquidity_min:
            continue

        price_change = matched_asset.get("price_change_percentage_24h", 0) or 0
        historical = fetch_historical_data(matched_asset['id'], days=30)
        true_prob = estimate_true_prob_advanced(price_change, matched_asset['id'], historical, use_sentiment, use_igarch)
        edge = compute_market_edge(yes_price, true_prob)

        if abs(edge) >= threshold:
            kelly = kelly_fraction(edge, 1 / yes_price if yes_price > 0 else 1)
            confidence = 0.8 if historical else 0.5
            if use_igarch and len(historical) > 1:
                returns = np.diff(historical) / historical[:-1]
                params = fit_igarch(returns)
                vol = igarch_vol(returns, params)
                confidence -= vol * 0.2
            confidence = np.clip(confidence, 0.3, 1.0)
            edges.append({
                "market_id": market.get("condition_id", market.get("id", "")),
                "question": market.get("question", ""),
                "asset": matched_asset.get("symbol", "").upper(),
                "yes_price": yes_price,
                "implied_prob_pct": estimate_prob(yes_price),
                "estimated_true_prob_pct": round(true_prob * 100, 2),
                "edge": round(edge, 4),
                "edge_pct": round(edge * 100, 2),
                "kelly_fraction": round(kelly, 4),
                "liquidity": liquidity,
                "price_change_24h": round(price_change, 2),
                "current_price_usd": matched_asset.get("current_price", 0),
                "confidence": round(confidence, 2),
            })

    edges.sort(key=lambda x: abs(x["edge"]), reverse=True)
    logger.info(f"Found {len(edges)} edges (threshold={threshold*100:.1f}%)")
    return edges

def backtest_edges(assets: List[str], days: int, threshold: float, use_igarch=True):
    results = []
    for asset in assets:
        historical = fetch_historical_data(asset, days)
        if not historical or len(historical) < 2:
            continue
        simulated_edges = []
        for i in range(30, len(historical)):
            window = historical[i-30:i]
            price_change = (historical[i] - historical[i-1]) / historical[i-1] * 100
            true_prob = estimate_true_prob_advanced(price_change, asset, window, use_sentiment=False, use_igarch=use_igarch)
            mock_market = true_prob - np.random.uniform(-0.1, 0.1)
            edge = true_prob - mock_market
            if abs(edge) > threshold:
                simulated_edges.append(edge)
        avg_roi = np.mean(simulated_edges) * 100 if simulated_edges else 0
        results.append({"asset": asset, "edges_found": len(simulated_edges), "avg_roi": avg_roi, "edge": np.mean(simulated_edges) if simulated_edges else 0})
    return results
