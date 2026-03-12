import math
import logging
import time
import functools
from typing import Optional
from .config import config
import numpy as np

def setup_logging():
    handlers = [logging.StreamHandler()]
    if config.log_file:
        handlers.append(logging.FileHandler(config.log_file))
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )

def estimate_prob(price: float) -> float:
    return round(price * 100, 2)

def kelly_fraction(edge: float, odds: float) -> float:
    if odds <= 0:
        return 0.0
    return max(0.0, edge / odds)

def retry(max_retries: int = None, delay: float = None):
    retries = max_retries if max_retries is not None else config.max_retries
    wait = delay if delay is not None else config.retry_delay_seconds

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import requests as _requests
            attempts = 0
            backoff = 2.0
            while True:
                try:
                    return func(*args, **kwargs)
                except _requests.exceptions.HTTPError as e:
                    if e.response is not None and e.response.status_code == 429:
                        attempts += 1
                        if attempts >= 6:
                            raise
                        sleep_time = min(backoff, 60.0)
                        backoff *= 2
                        time.sleep(sleep_time)
                    else:
                        attempts += 1
                        if attempts >= retries:
                            raise
                        time.sleep(wait)
                except Exception:
                    attempts += 1
                    if attempts >= retries:
                        raise
                    time.sleep(wait)
        return wrapper
    return decorator

COIN_ID_MAP = {
    "btc": "bitcoin", "sol": "solana",
    "doge": "dogecoin", "bnb": "binancecoin", "xrp": "ripple",
    "ada": "cardano", "avax": "avalanche-2", "matic": "matic-network",
}

def normalize_asset_id(name: str) -> str:
    cleaned = name.strip().lower()
    return COIN_ID_MAP.get(cleaned, cleaned)

def monte_carlo_sim(edges: np.array, trials: int = 1000):
    if len(edges) == 0:
        return {"win_prob": 0.0, "avg_return": 0.0}
    outcomes = np.random.normal(edges, np.std(edges) * 0.5, (trials, len(edges)))
    win_prob = np.mean(outcomes > 0)
    avg_return = np.mean(outcomes)
    return {"win_prob": win_prob, "avg_return": avg_return}
