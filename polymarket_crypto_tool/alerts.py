import logging
import os
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

def _edge_to_discord_embed(edge: Dict) -> Dict:
    direction = "OVER" if edge["edge"] > 0 else "UNDER"
    color = 0x00FF88 if edge["edge"] > 0 else 0xFF4444
    return {
        "title": f"[{edge['asset']}] Edge Detected: {edge['edge_pct']:+.2f}%",
        "description": edge["question"][:200],
        "color": color,
        "fields": [
            {"name": "Direction", "value": direction, "inline": True},
            {"name": "Yes Price", "value": f"{edge['yes_price']:.3f}", "inline": True},
            {"name": "Est. True Prob", "value": f"{edge['estimated_true_prob_pct']:.1f}%", "inline": True},
            {"name": "Edge", "value": f"{edge['edge_pct']:+.2f}%", "inline": True},
            {"name": "Kelly Fraction", "value": f"{edge['kelly_fraction']:.4f}", "inline": True},
            {"name": "Liquidity", "value": f"${edge['liquidity']:,.0f}", "inline": True},
            {"name": "24h Price Change", "value": f"{edge['price_change_24h']:+.2f}%", "inline": True},
            {"name": "Spot Price", "value": f"${edge['current_price_usd']:,.2f}", "inline": True},
        ],
        "footer": {"text": f"Market ID: {edge['market_id']}"},
    }

def send_discord_alert(edges: List[Dict], webhook_url: str = "", max_alerts: int = 5) -> bool:
    url = webhook_url or DISCORD_WEBHOOK_URL
    if not url or not edges:
        return False
    top = edges[:max_alerts]
    embeds = [_edge_to_discord_embed(e) for e in top]
    payload = {
        "username": "Polymarket Edge Bot",
        "content": f"**{len(top)} edge(s) found** above threshold",
        "embeds": embeds,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code in (200, 204)
    except:
        return False

def send_slack_alert(edges: List[Dict], webhook_url: str = "", max_alerts: int = 5) -> bool:
    url = webhook_url or SLACK_WEBHOOK_URL
    if not url or not edges:
        return False
    top = edges[:max_alerts]
    blocks = [{"type": "header", "text": {"type": "plain_text", "text": f"Polymarket Edge Alert: {len(top)} opportunities"}}]
    payload = {"blocks": blocks}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except:
        return False

def send_alerts(edges: List[Dict], discord_url: str = "", slack_url: str = "", max_alerts: int = 5) -> Dict[str, bool]:
    return {
        "discord": send_discord_alert(edges, discord_url, max_alerts),
        "slack": send_slack_alert(edges, slack_url, max_alerts),
    }
