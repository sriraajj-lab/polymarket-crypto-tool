import os
from dataclasses import dataclass, field
from typing import List


def _parse_list(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass
class Config:
    polymarket_api_base: str = os.environ.get("POLYMARKET_API_BASE", "https://clob.polymarket.com")
    coingecko_api_base: str = os.environ.get("COINGECKO_API_BASE", "https://api.coingecko.com/api/v3")
    coingecko_api_key: str = os.environ.get("COINGECKO_API_KEY", "")
    poll_interval_seconds: int = int(os.environ.get("POLL_INTERVAL_SECONDS", "60"))
    request_timeout_seconds: int = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "15"))
    edge_threshold: float = float(os.environ.get("EDGE_THRESHOLD", "0.05"))
    min_liquidity: float = float(os.environ.get("MIN_LIQUIDITY", "1000.0"))
    tracked_assets: List[str] = field(
        default_factory=lambda: _parse_list(
            os.environ.get("TRACKED_ASSETS", "bitcoin,ethereum,solana,dogecoin")
        )
    )
    output_format: str = os.environ.get("OUTPUT_FORMAT", "table")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_file: str = os.environ.get("LOG_FILE", "")
    discord_webhook_url: str = os.environ.get("DISCORD_WEBHOOK_URL", "")
    slack_webhook_url: str = os.environ.get("SLACK_WEBHOOK_URL", "")
    alert_max_edges: int = int(os.environ.get("ALERT_MAX_EDGES", "5"))
    max_retries: int = int(os.environ.get("MAX_RETRIES", "3"))
    retry_delay_seconds: float = float(os.environ.get("RETRY_DELAY_SECONDS", "1.0"))


config = Config()
