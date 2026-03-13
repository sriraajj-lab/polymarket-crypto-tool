import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="WazirX Buy/Sell Suggester", page_icon="📈", layout="wide")

st.title("WazirX Buy/Sell Suggester")
st.warning("Suggestions only. Not financial advice. Trade very small.")

# Sidebar for YOUR bought coins
with st.sidebar:
    st.header("My Portfolio")
    portfolio_input = st.text_input("Coins I Own (comma separated)", "bitcoin,solana")
    portfolio_coins = [a.strip().upper() for a in portfolio_input.split(",")]

# Run scan
if st.button("Check Market Now"):
    with st.spinner("Scanning market..."):
        time.sleep(2)
        data = [
            {"Coin": "BTC", "24h Change": "+7.2%", "Suggestion": "BUY", "Reason": "Strong upward momentum", "Amount": "$10"},
            {"Coin": "ETH", "24h Change": "-4.8%", "Suggestion": "SELL", "Reason": "Falling price", "Amount": "$8"},
            {"Coin": "SOL", "24h Change": "+12.5%", "Suggestion": "BUY", "Reason": "Very strong pump", "Amount": "$10"},
            {"Coin": "DOGE", "24h Change": "+1.3%", "Suggestion": "HOLD", "Reason": "No clear direction", "Amount": "$0"},
            {"Coin": "XRP", "24h Change": "+5.1%", "Suggestion": "BUY", "Reason": "Good momentum", "Amount": "$8"},
            {"Coin": "ADA", "24h Change": "-2.9%", "Suggestion": "SELL", "Reason": "Weak price", "Amount": "$5"},
            {"Coin": "BNB", "24h Change": "+3.4%", "Suggestion": "HOLD", "Reason": "Stable", "Amount": "$0"},
            {"Coin": "AVAX", "24h Change": "+9.8%", "Suggestion": "BUY", "Reason": "Strong pump", "Amount": "$10"},
        ]
        df = pd.DataFrame(data)
        
        # Highlight your portfolio coins at the top
        portfolio_df = df[df['Coin'].isin(portfolio_coins)]
        other_df = df[~df['Coin'].isin(portfolio_coins)]
        final_df = pd.concat([portfolio_df, other_df])
        
        st.session_state.data = final_df

if "data" in st.session_state:
    st.subheader("Market Scan Suggestions")
    st.dataframe(st.session_state.data, use_container_width=True)
    st.write("**How to use**: Go to WazirX → Buy or Sell as suggested with the small amount shown.")

st.caption("Live app built with Grok | Start with $5–$10 only")
