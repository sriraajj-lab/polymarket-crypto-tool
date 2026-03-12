import streamlit as st
import pandas as pd
import time
import logging

from polymarket_crypto_tool.config import Config
from polymarket_crypto_tool.fetchers import fetch_polymarket_markets, fetch_crypto_market_data
from polymarket_crypto_tool.analyzers import find_edges
from polymarket_crypto_tool.alerts import send_alerts

st.set_page_config(page_title="Polymarket Crypto Edge Pro", page_icon="📈", layout="wide")

st.title("Polymarket Crypto Edge Pro")
st.warning("Sim mode only. Not financial advice.")

cfg = Config()

# Sidebar
with st.sidebar:
    st.header("Configuration")
    tracked_assets_str = st.text_input("Tracked Assets", ",".join(cfg.tracked_assets))
    cfg.tracked_assets = [a.strip() for a in tracked_assets_str.split(",") if a.strip()]
    cfg.edge_threshold = st.slider("Edge Threshold", 0.01, 0.50, cfg.edge_threshold, 0.01)
    cfg.min_liquidity = st.number_input("Min Liquidity (USD)", 100.0, value=cfg.min_liquidity)

# Run scan
if st.button("Run Single Scan"):
    with st.spinner("Scanning markets..."):
        markets = []
        for asset in cfg.tracked_assets:
            markets.extend(fetch_polymarket_markets(keyword=asset))
        crypto_data = fetch_crypto_market_data(cfg.tracked_assets)
        edges = find_edges(markets, crypto_data, cfg.edge_threshold, cfg.min_liquidity)
        st.session_state.edges = edges
    st.success(f"Found {len(edges)} edges!")

# Display results
if "edges" in st.session_state and st.session_state.edges:
    df = pd.DataFrame(st.session_state.edges)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No edges yet. Click 'Run Single Scan' to start.")

st.caption("Live app built with Grok")
