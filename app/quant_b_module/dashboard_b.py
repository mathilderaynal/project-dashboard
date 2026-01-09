import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os

from data_manager import PortfolioDataManager
from portfolio_manager import PortfolioSimulator

def run_quant_b_dashboard():
    st.title("💰 Multi-Asset Portfolio Manager")
    st.markdown("### Interactive Backtesting & Correlation Analysis")

    # --- SIDEBAR: AUTO-REFRESH SYSTEM ---
    st.sidebar.header("⚙️ Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh (5m)")
    
    if auto_refresh:
        # Wait 300 seconds (5 mins) then reload the page
        time.sleep(300)
        st.rerun()

    # --- SIDEBAR: REPORT VIEWER ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Daily Reports Archive")
    
    # Logic to find and read reports from 'data_reports' folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '../../'))
    report_dir = os.path.join(project_root, "data_reports")
    
    if os.path.exists(report_dir):
        files = sorted(os.listdir(report_dir), reverse=True) # Newest first
        if files:
            selected_file = st.sidebar.selectbox("Select Report:", files)
            if selected_file:
                file_path = os.path.join(report_dir, selected_file)
                with open(file_path, "r") as f:
                    report_content = f.read()
                
                # Display content in an expandable box
                with st.sidebar.expander("View Report Content", expanded=True):
                    st.text(report_content)
        else:
            st.sidebar.info("No reports generated yet.")
    else:
        st.sidebar.warning("Report directory not found.")

    st.sidebar.markdown("---")

    # --- STANDARD DASHBOARD LOGIC BELOW ---
    st.sidebar.header("Strategy Parameters")
    
    default_tickers = ['AAPL', 'BTC-USD', 'GLD', 'MSFT', 'EURUSD=X']
    selected_tickers = st.sidebar.multiselect(
        "Select Assets (Min 3)", 
        options=default_tickers, 
        default=['AAPL', 'BTC-USD', 'GLD']
    )

    if len(selected_tickers) < 3:
        st.error("Please select at least 3 assets.")
        return

    # Settings
    interval = st.sidebar.selectbox("Data Frequency", ["15m", "1h", "1d"], index=0)
    period_map = {"15m": "5d", "1h": "1mo", "1d": "1y"}
    selected_period = period_map[interval]

    strategy_type = st.sidebar.radio(
        "Strategy Type",
        ["Constant Rebalancing (Fixed Weights)", "Buy & Hold (Drifting Weights)"]
    )
    should_rebalance = True if "Constant" in strategy_type else False

    st.sidebar.subheader("Initial Allocation")
    weights = {}
    for ticker in selected_tickers:
        weights[ticker] = st.sidebar.slider(f"{ticker}", 0.0, 1.0, 1.0/len(selected_tickers))
    
    total = sum(weights.values())
    if total > 0:
        weights = {k: v/total for k, v in weights.items()}

    # Trigger: Button OR Auto-Refresh
    if st.sidebar.button("Run Simulation") or auto_refresh:
        
        manager = PortfolioDataManager(selected_tickers)
        with st.spinner(f"Fetching {interval} data..."):
            # Fetch fresh data
            df = manager.fetch_live_data(period=selected_period, interval=interval)
            
            if df.empty:
                st.error("No data. Market closed?")
                return

            sim = PortfolioSimulator(df)
            cumulative_return = sim.simulate_portfolio(weights, rebalance=should_rebalance)
            
            if cumulative_return.empty:
                st.error("Simulation failed.")
                return

            metrics = sim.get_metrics()

            # Visualization
            st.subheader("📈 Portfolio vs. Assets Performance")
            
            filled_df = df.ffill().bfill()
            normalized_assets = (filled_df / filled_df.iloc[0]) * 100
            
            fig = go.Figure()

            # Assets
            for ticker in selected_tickers:
                fig.add_trace(go.Scatter(
                    x=normalized_assets.index, y=normalized_assets[ticker],
                    mode='lines', name=ticker, opacity=0.7, line=dict(width=1.5), connectgaps=True 
                ))

            # Portfolio
            fig.add_trace(go.Scatter(
                x=cumulative_return.index, y=cumulative_return,
                mode='lines', name='PORTFOLIO', line=dict(color='black', width=2), connectgaps=True
            ))

            fig.update_layout(
                xaxis_title="Date", yaxis_title="Value (Base=100)",
                height=500, hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
            )
            st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)
            c1.metric("Total Return", f"{metrics['total_return']:.2%}")
            c2.metric("Volatility (Ann.)", f"{metrics['volatility']:.2%}")

            st.subheader("Correlation Matrix")
            fig_corr = px.imshow(metrics['correlation'], text_auto=True, aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
            st.plotly_chart(fig_corr)

if __name__ == "__main__":
    run_quant_b_dashboard()
