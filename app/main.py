import streamlit as st
import matplotlib.pyplot as plt

from core.data import fetch_price_history


st.set_page_config(page_title="Project Dashboard", layout="wide")
st.title("Project Dashboard")
st.subheader("Quant A — Single Asset (Data check)")

# --- Sidebar controls ---
st.sidebar.header("Settings")

symbol = st.sidebar.selectbox("Asset", ["BTC-USD", "EURUSD=X", "AAPL"])
period = st.sidebar.selectbox("Lookback period", ["1mo", "3mo", "6mo", "1y"])
interval = st.sidebar.selectbox("Interval", ["1d", "1h"])

# --- Fetch data ---
df = fetch_price_history(symbol, period=period, interval=interval)

# --- Display raw data ---
st.write("Latest rows")
st.dataframe(df.tail(10))

# --- Plot Close price ---
st.write("Close price")

fig, ax = plt.subplots()
ax.plot(df.index, df["Close"])
ax.set_title(f"{symbol} — Close price")
ax.set_xlabel("Date")
ax.set_ylabel("Price")

st.pyplot(fig)
