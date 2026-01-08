import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Import our custom classes
from data_manager import PortfolioDataManager
from portfolio_manager import PortfolioSimulator

def run_quant_b_dashboard():
    st.title("💰 Multi-Asset Portfolio Manager")
    st.markdown("### Interactive Backtesting & Correlation Analysis")

    # --- SIDEBAR: User Controls  ---
    st.sidebar.header("Strategy Parameters")
    
    # 1. Asset Selection
    default_tickers = ['AAPL', 'BTC-USD', 'GLD', 'MSFT', 'EURUSD=X']
    selected_tickers = st.sidebar.multiselect(
        "Select Assets (Min 3)", 
        options=default_tickers, 
        default=['AAPL', 'BTC-USD', 'GLD']
    )

    if len(selected_tickers) < 3:
        st.error("Please select at least 3 assets as per project requirements.")
        return

    # 2. Weight Allocation
    st.sidebar.subheader("Asset Allocation")
    weights = {}
    for ticker in selected_tickers:
        # Default equal weight roughly
        default_w = 1.0 / len(selected_tickers)
        weights[ticker] = st.sidebar.slider(f"Weight: {ticker}", 0.0, 1.0, default_w)

    # 3. Refresh Rate (Data fetching)
    # Using Streamlit cache to handle the "refresh every 5 mins" requirement 
    @st.cache_data(ttl=300)  # 300 seconds = 5 minutes
    def get_cached_data(tickers):
        manager = PortfolioDataManager(tickers)
        return manager.fetch_live_data(period="5d", interval="15m")

    # --- MAIN LOGIC ---
    if st.sidebar.button("Run Simulation"):
        with st.spinner("Fetching live market data..."):
            # Fetch Data
            df = get_cached_data(selected_tickers)
            
            if df.empty:
                st.error("No data returned. Market might be closed or API down.")
                return

            # Run Simulation
            sim = PortfolioSimulator(df)
            cumulative_return = sim.simulate_portfolio(weights)
            metrics = sim.get_metrics()

            # --- VISUALIZATION [cite: 20, 44] ---
            
            # 1. Main Chart: Portfolio vs Individual Assets
            st.subheader("Performance Comparison")
            
            # Normalize individual assets to start at 100 for fair comparison
            normalized_assets = df / df.iloc[0] * 100
            
            # Combine Portfolio curve with Assets
            chart_data = normalized_assets.copy()
            chart_data['PORTFOLIO'] = cumulative_return
            
            st.line_chart(chart_data)

            # 2. Key Metrics
            st.subheader("Risk & Return Metrics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Portfolio Volatility (Ann.)", f"{metrics['volatility'].mean():.2%}")
            
            with col2:
                final_return = (cumulative_return.iloc[-1] - 100)
                st.metric("Total Return (Period)", f"{final_return:.2f}%")

            # 3. Correlation Matrix [cite: 42]
            st.subheader("Correlation Matrix")
            st.write("Heatmap of asset correlations:")
            
            # Use Plotly for a better heatmap
            fig = px.imshow(
                metrics['correlation'], 
                text_auto=True, 
                aspect="auto",
                color_continuous_scale="RdBu_r"
            )
            st.plotly_chart(fig)

            # Display Raw Data (Optional but good for debugging)
            with st.expander("View Raw Data"):
                st.dataframe(df.tail())

# This allows us to run this module independently for testing
if __name__ == "__main__":
    run_quant_b_dashboard()
