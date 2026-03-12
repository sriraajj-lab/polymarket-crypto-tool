import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Polymarket Crypto Edge Pro", page_icon="📈", layout="wide")

st.title("Polymarket Crypto Edge Pro")
st.warning("Sim mode only. Not financial advice.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    assets = st.text_input("Tracked Assets", "bitcoin,ethereum,solana")
    threshold = st.slider("Edge Threshold", 0.01, 0.50, 0.05)
    min_liq = st.number_input("Min Liquidity (USD)", value=1000.0)

# Run scan
if st.button("Run Single Scan"):
    with st.spinner("Scanning markets..."):
        time.sleep(2)  # Simulate scan
        # Mock data for testing
        data = [
            {"asset": "BTC", "edge_pct": 12.5, "yes_price": 0.45, "liquidity": 45000},
            {"asset": "ETH", "edge_pct": -8.3, "yes_price": 0.62, "liquidity": 12000},
        ]
        df = pd.DataFrame(data)
        st.session_state.edges = df
    st.success("Scan complete!")

# Show results
if "edges" in st.session_state:
    st.dataframe(st.session_state.edges, use_container_width=True)
    st.subheader("Portfolio Sim")
    st.write("Simulated $10 trade PNL: +$1.25 (example)")
else:
    st.info("Click 'Run Single Scan' to start.")

st.caption("Live app built with Grok")
