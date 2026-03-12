import time
import requests
import logging
from typing import List, Dict
from .config import config
from .utils import retry, normalize_asset_id
import os
import joblib
from functools import lru_cache
logger = logging.getLogger(__name__)

@retry()
def fetch_polymarket_markets(keyword: str = "") -> List[Dict]:
    url = f"{config.polymarket_api_base}/markets"
    params = {"active": "true", "closed": "false"}
    if keyword:
        params["search"] = keyword
    resp = requests.get(url, params=params, timeout=config.request_timeout_seconds)
    if resp.status_code != 200:
        logger.warning(f"Polymarket API returned {resp.status_code} for keyword='{keyword}'")
        return []
    data = resp.json()
    return data.get("data", data) if isinstance(data, dict) else data

@retry()
def fetch_market_orderbook(market_id: str) -> Dict:
    url = f"{config.polymarket_api_base}/book"
    params = {"token_id": market_id}
    resp = requests.get(url, params=params, timeout=config.request_timeout_seconds)
    resp.raise_for_status()
    return resp.json()

@retry()
def fetch_crypto_prices(asset_ids: List[str]) -> Dict[str, float]:
    normalized = [normalize_asset_id(a) for a in asset_ids]
    ids_str = ",".join(normalized)
    url = f"{config.coingecko_api_base}/simple/price"
    params = {"ids": ids_str, "vs_currencies": "usd"}
    headers = {}
    if config.coingecko_api_key:
        headers["x-cg-demo-api-key"] = config.coingecko_api_key
    time.sleep(2)
    resp = requests.get(url, params=params, headers=headers, timeout=config.request_timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    return {k: v["usd"] for k, v in data.items() if "usd" in v}

@retry()
def fetch_crypto_market_data(asset_ids: List[str]) -> List[Dict]:
    normalized = [normalize_asset_id(a) for a in asset_ids]
    ids_str = ",".join(normalized)
    url = f"{config.coingecko_api_base}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids_str,
        "order": "market_cap_desc",
        "sparkline": "false",
        "price_change_percentage": "24h",
    }
    headers = {}
    if config.coingecko_api_key:
        headers["x-cg-demo-api-key"] = config.coingecko_api_key
    time.sleep(2)
    resp = requests.get(url, params=params, headers=headers, timeout=config.request_timeout_seconds)
    resp.raise_for_status()
    return resp.json()

@lru_cache(maxsize=32)
def fetch_historical_data(asset_id: str, days: int = 30) -> List[float]:
    cache_file = f"{asset_id}_{days}_historical.cache"
    if os.path.exists(cache_file):
        return joblib.load(cache_file)
    normalized = normalize_asset_id(asset_id)
    url = f"{config.coingecko_api_base}/coins/{normalized}/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    headers = {}
    if config.coingecko_api_key:
        headers["x-cg-demo-api-key"] = config.coingecko_api_key
    time.sleep(2)
    resp = requests.get(url, params=params, headers=headers, timeout=config.request_timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    prices = [p[1] for p in data.get("prices", []) if p]
    joblib.dump(prices, cache_file)
    return prices

def fetch_kalshi_data():
    return [{"market": "Kalshi Mock Event", "prob": 0.55}]
def fetch_x_sentiment(asset: str) -> List[Dict]:
    # Placeholder for X sentiment (can be replaced with real API later)
    return [{"content": f"Positive on {asset}"} for _ in range(5)]
