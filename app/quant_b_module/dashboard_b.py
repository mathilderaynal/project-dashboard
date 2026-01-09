import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_manager import PortfolioDataManager
from portfolio_manager import PortfolioSimulator

def run_quant_b_dashboard():
    st.title("💰 Multi-Asset Portfolio Manager")
    st.markdown("### Interactive Backtesting & Correlation Analysis")

    # --- SIDEBAR: User Controls ---
    st.sidebar.header("Strategy Parameters")
    
    # 1. Asset Selection
    default_tickers = ['AAPL', 'BTC-USD', 'GLD', 'MSFT', 'EURUSD=X']
    selected_tickers = st.sidebar.multiselect(
        "Select Assets (Min 3)", 
        options=default_tickers, 
        default=['AAPL', 'BTC-USD', 'GLD']
    )

    if len(selected_tickers) < 3:
        st.error("Please select at least 3 assets.")
        return

    # 2. Strategy Settings
    st.sidebar.subheader("Simulation Settings")
    
    # Frequency Selector
    interval = st.sidebar.selectbox("Data Frequency", ["15m", "1h", "1d"], index=0)
    period_map = {"15m": "5d", "1h": "1mo", "1d": "1y"}
    selected_period = period_map[interval]

    # Rebalancing Toggle
    strategy_type = st.sidebar.radio(
        "Strategy Type",
        ["Constant Rebalancing (Fixed Weights)", "Buy & Hold (Drifting Weights)"]
    )
    should_rebalance = True if "Constant" in strategy_type else False

    # 3. Weight Allocation
    st.sidebar.subheader("Initial Allocation")
    weights = {}
    for ticker in selected_tickers:
        weights[ticker] = st.sidebar.slider(f"{ticker}", 0.0, 1.0, 1.0/len(selected_tickers))
    
    # Normalize weights
    total = sum(weights.values())
    if total > 0:
        weights = {k: v/total for k, v in weights.items()}

    # --- DATA FETCHING ---
    @st.cache_data(ttl=300)
    def get_cached_data(tickers, p, i):
        manager = PortfolioDataManager(tickers)
        return manager.fetch_live_data(period=p, interval=i)

    # --- MAIN LOGIC ---
    if st.sidebar.button("Run Simulation"):
        with st.spinner(f"Fetching {interval} data..."):
            df = get_cached_data(selected_tickers, selected_period, interval)
            
            if df.empty:
                st.error("No data. Market closed?")
                return

            sim = PortfolioSimulator(df)
            cumulative_return = sim.simulate_portfolio(weights, rebalance=should_rebalance)
            
            if cumulative_return.empty:
                st.error("Simulation failed.")
                return

            metrics = sim.get_metrics()

            # --- VISUALIZATION: FIXED NORMALIZATION & THINNER LINE ---
            st.subheader("📈 Portfolio vs. Assets Performance")
            
            # CRITICAL FIX: Backfill first so we have a valid starting price for Stocks
            # .ffill() handles gaps in the middle
            # .bfill() handles gaps at the very start (e.g., Sunday night)
            filled_df = df.ffill().bfill()
            
            # Now Normalize: (Price / Start_Price) * 100
            # This ensures ALL lines start exactly at 100.
            normalized_assets = (filled_df / filled_df.iloc[0]) * 100
            
            # Create Custom Plotly Chart
            fig = go.Figure()

            # 1. Add Assets (Rainbow colors)
            for ticker in selected_tickers:
                fig.add_trace(go.Scatter(
                    x=normalized_assets.index,
                    y=normalized_assets[ticker],
                    mode='lines',
                    name=ticker,
                    opacity=0.7,
                    line=dict(width=1.5),
                    connectgaps=True 
                ))

            # 2. Add Portfolio (THINNER BLACK LINE)
            fig.add_trace(go.Scatter(
                x=cumulative_return.index,
                y=cumulative_return,
                mode='lines',
                name='PORTFOLIO',
                # Changed width from 4 to 2 (Thinner)
                line=dict(color='black', width=2), 
                connectgaps=True
            ))

            # 3. Clean Layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Value (Base=100)",
                height=500,
                hovermode="x unified",
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                    bgcolor="rgba(255, 255, 255, 0.8)"
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- METRICS ---
            c1, c2 = st.columns(2)
            c1.metric("Total Return", f"{metrics['total_return']:.2%}")
            c2.metric("Volatility (Ann.)", f"{metrics['volatility']:.2%}")

            # --- CORRELATION ---
            st.subheader("Correlation Matrix")
            fig_corr = px.imshow(
                metrics['correlation'],
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1
            )
            st.plotly_chart(fig_corr)

if __name__ == "__main__":
    run_quant_b_dashboard()
