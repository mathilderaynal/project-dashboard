import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Ensure we can import modules regardless of where the script is run from
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '../../'))

from app.quant_b_module.data_manager import PortfolioDataManager
from app.quant_b_module.portfolio_manager import PortfolioSimulator

def generate_daily_report():
    # 1. Define assets to track
    tickers = ['AAPL', 'BTC-USD', 'GLD', 'MSFT', 'EURUSD=X']
    print(f"Generating report for: {tickers}")

    # 2. Fetch Data (Last 5 days for recent context)
    manager = PortfolioDataManager(tickers)
    df = manager.fetch_live_data(period="5d", interval="15m")

    if df.empty:
        print("Error: No data fetched.")
        return

    # 3. Run Simulation (Equal Weights) to get Portfolio Metrics
    sim = PortfolioSimulator(df)
    weights = {t: 1.0/len(tickers) for t in tickers}
    cumulative_return = sim.simulate_portfolio(weights, rebalance=True)
    metrics = sim.get_metrics()

    # 4. Calculate Max Drawdown
    # (Peak so far - Current Value) / Peak so far
    roll_max = cumulative_return.cummax()
    drawdown = cumulative_return / roll_max - 1.0
    max_drawdown = drawdown.min()

    # 5. Format the Report
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_content = f"""
=========================================
DAILY PORTFOLIO REPORT - QUANT B
Date: {today}
=========================================

[RISK METRICS (Last 5 Days)]
Annualized Volatility: {metrics['volatility'].mean():.2%}
Max Drawdown:          {max_drawdown:.2%}
Total Return:          {metrics['total_return']:.2%}

[ASSET SNAPSHOT (Latest Close)]
"""
    # Add individual asset prices
    last_prices = df.ffill().iloc[-1]
    for ticker in tickers:
        price = last_prices.get(ticker, "N/A")
        val = f"${price:.2f}" if isinstance(price, (int, float)) else price
        report_content += f"- {ticker}: {val}\n"

    report_content += "\n=========================================\n"

    # 6. Save to 'data_reports' folder in project root
    project_root = os.path.abspath(os.path.join(current_dir, '../../'))
    report_dir = os.path.join(project_root, "data_reports")

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    filename = f"{report_dir}/report_{datetime.now().strftime('%Y%m%d')}.txt"

    with open(filename, "w") as f:
        f.write(report_content)

    print(f"Report saved: {filename}")

if __name__ == "__main__":
    generate_daily_report()
