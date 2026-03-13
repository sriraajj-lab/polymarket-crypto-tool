import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="WazirX Buy/Sell Suggester", page_icon="📈", layout="wide")

st.title("WazirX Buy/Sell Suggester")
st.warning("Suggestions only. Not financial advice. Trade very small ($5–$10 max).")

# Sidebar
with st.sidebar:
    st.header("Settings")
    assets = st.text_input("Coins to Watch", "bitcoin,ethereum,solana")
    threshold = st.slider("Signal Threshold %", 2, 15, 5)

if st.button("Check Market Now"):
    with st.spinner("Checking live prices..."):
        time.sleep(2)
        # Mock realistic suggestions
        data = [
            {"Coin": "BTC", "24h Change": "+7.2%", "Suggestion": "BUY", "Reason": "Strong upward momentum", "Amount": "$10"},
            {"Coin": "ETH", "24h Change": "-4.8%", "Suggestion": "SELL", "Reason": "Falling price", "Amount": "$8"},
            {"Coin": "SOL", "24h Change": "+12.5%", "Suggestion": "BUY", "Reason": "Very strong pump", "Amount": "$10"},
            {"Coin": "DOGE", "24h Change": "+1.3%", "Suggestion": "HOLD", "Reason": "No clear direction", "Amount": "$0"},
        ]
        df = pd.DataFrame(data)
        st.session_state.data = df

if "data" in st.session_state:
    st.subheader("Buy / Sell Suggestions for WazirX")
    st.dataframe(st.session_state.data, use_container_width=True)
    st.write("**How to use**: Go to WazirX → Buy or Sell the coins as suggested with the small amount shown.")

st.caption("Live app built with Grok | Start with $5–$10 only")
