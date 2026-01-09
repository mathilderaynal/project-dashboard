import streamlit as st
import matplotlib.pyplot as plt
from core.data import fetch_price_history
import numpy as np


def run_quant_a_dashboard():
    
    
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
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    ## buy and hold
    
    
    st.write("Buy & Hold — cumulative value (starting at 100)")
    
    # daily/period returns from Close
    returns = df["Close"].pct_change().dropna()
    
    # equity curve starting at 100
    equity_bh = 100 * (1 + returns).cumprod()
    
    fig2, ax2 = plt.subplots()
    ax2.plot(equity_bh.index, equity_bh.values)
    ax2.set_title("Buy & Hold — Equity curve")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Value")
    plt.xticks(rotation=45)
    st.pyplot(fig2)
    
    ## ajout des metriques de performance 
    st.write("Buy & Hold — Performance metrics")
    
    # Total return
    total_return = equity_bh.iloc[-1] / equity_bh.iloc[0] - 1
    
    # Max drawdown
    rolling_max = equity_bh.cummax()
    drawdown = (equity_bh - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Return", f"{total_return:.2%}")
    col2.metric("Max Drawdown", f"{max_drawdown:.2%}")
    
    # Sharpe ratio (assuming risk-free rate = 0)
    sharpe = returns.mean() / returns.std() * (252 ** 0.5)
    
    col3 = st.columns(1)[0]
    col3.metric("Sharpe Ratio", f"{sharpe:.2f}")
    
    ## Ajout strategie 
    st.divider()
    st.subheader("Strategy 2 — Moving Average Crossover")
    
    # --- Parameters ---
    short_window = st.slider("Short MA window", min_value=2, max_value=50, value=10)
    long_window = st.slider("Long MA window", min_value=10, max_value=200, value=30)
    
    if short_window >= long_window:
        st.error("Short window must be strictly smaller than long window.")
    else:
        # --- Signals ---
        close = df["Close"].copy()
        ma_short = close.rolling(short_window).mean()
        ma_long = close.rolling(long_window).mean()
    
        signal = (ma_short > ma_long).astype(int)          # 1 = long, 0 = cash
        position = signal.shift(1).fillna(0)               # trade on next bar (no look-ahead)
    
        strat_returns = returns * position.loc[returns.index]
    
        equity_ma = 100 * (1 + strat_returns).cumprod()
    
        # --- Plot: compare equity curves ---
        st.write("Equity curves (start at 100)")
    
        fig3, ax3 = plt.subplots()
        ax3.plot(equity_bh.index, equity_bh.values, label="Buy & Hold")
        ax3.plot(equity_ma.index, equity_ma.values, label="MA Crossover")
        ax3.set_title("Buy & Hold vs MA Crossover")
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Value")
        ax3.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig3)
    
        # --- Metrics for MA strategy ---
        total_return_ma = equity_ma.iloc[-1] / equity_ma.iloc[0] - 1
    
        rolling_max_ma = equity_ma.cummax()
        drawdown_ma = (equity_ma - rolling_max_ma) / rolling_max_ma
        max_drawdown_ma = drawdown_ma.min()
    
        col1, col2 = st.columns(2)
        col1.metric("MA Total Return", f"{total_return_ma:.2%}")
        col2.metric("MA Max Drawdown", f"{max_drawdown_ma:.2%}")


if __name__ == '__main__':
    run_quant_a_dashboard()
