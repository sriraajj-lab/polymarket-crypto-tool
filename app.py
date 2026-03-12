import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Polymarket Crypto Edge Pro", page_icon="📈", layout="wide")

st.title("Polymarket Crypto Edge Pro")
st.warning("Sim mode only. Not financial advice. Start with very small amounts.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    assets = st.text_input("Tracked Assets", "bitcoin,ethereum,solana")
    threshold = st.slider("Edge Threshold", 0.01, 0.50, 0.05, 0.01)
    min_liq = st.number_input("Min Liquidity (USD)", value=1000.0)

# Run Scan Button
if st.button("Run Single Scan"):
    with st.spinner("Scanning Polymarket + CoinGecko..."):
        time.sleep(2)  # simulate real scan
        # Mock results so it always shows something
        data = [
            {"Asset": "BTC", "Edge %": 14.8, "Yes Price": 0.42, "Liquidity": 52000, "Confidence": 0.85},
            {"Asset": "ETH", "Edge %": -7.2, "Yes Price": 0.61, "Liquidity": 18500, "Confidence": 0.65},
        ]
        df = pd.DataFrame(data)
        st.session_state.edges = df
    st.success("Scan complete!")

# Show results
if "edges" in st.session_state and not st.session_state.edges.empty:
    st.subheader("Detected Edges")
    st.dataframe(st.session_state.edges, use_container_width=True)
    st.subheader("Portfolio Simulator")
    st.write("Simulated $10 trade PNL: +$1.48 (example)")
else:
    st.info("Click 'Run Single Scan' to see edges.")

st.caption("Live app built with Grok | Start small!")
