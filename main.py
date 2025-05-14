import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Load API key from Streamlit secrets
API_KEY = st.secrets["api_key"] 
BASE_URL = "https://stock.indianapi.in"

st.title("📈 EquiLens – TCS Stock Snapshot")

# Stock selection (fixed to TCS for now)
stock_name = "TCS"

# Headers for authentication
headers = {
    "X-API-KEY": API_KEY
}

# Fetch stock details
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(stock):
    response = requests.get(f"{BASE_URL}/stock", params={"name": stock}, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Fetch 1-month price history
@st.cache_data(ttl=3600)
def fetch_price_history(symbol):
    params = {
        "symbol": symbol,
        "period": "1m",
        "filter": "price"
    }
    response = requests.get(f"{BASE_URL}/historical_data", params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Step 1: Get current price + metrics
stock_data = fetch_stock_data(stock_name)

# Extract key details
nse_price = stock_data["currentPrice"].get("NSE")

# PE and PB are found under peerCompanyList[0]
#peer_data = stock_data.get("peerCompanyList", [])[0] if stock_data.get("peerCompanyList") else {}
pe = stock_data["companyProfile"]["peerCompanyList"][0].get("priceToEarningsValueRatio")
pb = stock_data["companyProfile"]["peerCompanyList"][0].get("priceToBookValueRatio")

col1, col2, col3 = st.columns(3)
col1.metric("📌 NSE Price", f"₹{nse_price}" if nse_price else "N/A")
col2.metric("📊 PE Ratio", f"{pe}" if pe else "N/A")
col3.metric("📘 PB Ratio", f"{pb}" if pb else "N/A")


# Step 2: Get 1-month price history
# Fix: Use correct ticker ID from peerCompanyList
ticker_id = peer_data.get("tickerId")

if ticker_id:
    history_data = fetch_price_history(ticker_id)
    if history_data and "datasets" in history_data and history_data["datasets"]:
        price_dataset = history_data["datasets"][0]["values"]
        df = pd.DataFrame(price_dataset, columns=["Date", "Price"])
        df["Date"] = pd.to_datetime(df["Date"])
        df["Price"] = df["Price"].astype(float)
        df.sort_values("Date", inplace=True)

        st.subheader("📆 Price History (1 Month)")
        st.line_chart(df.set_index("Date"))
    else:
        st.warning("No price history found.")

