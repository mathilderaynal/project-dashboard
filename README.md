# 🏦 Quantitative Asset Management & Analysis Platform

## 📖 Project Overview
This platform is a full-stack financial dashboard designed to bridge the gap between **Single-Asset Technical Analysis (Quant A)** and **Multi-Asset Portfolio Optimization (Quant B)**. Built on **Streamlit**, it leverages Python's data science stack to provide real-time market insights, strategy backtesting, and automated risk monitoring.

The system is deployed on a cloud environment (AWS EC2) and features a dual-module architecture to serve different investment horizons:
1.  **Quant A:** Active Trading & Technical Indicators.
2.  **Quant B:** Passive Investing, Diversification & Risk Management.

---

## 🏗️ System Architecture

### **Data Source & Extraction**
* **Source:** [Yahoo Finance](https://finance.yahoo.com)
* **Extraction Method:** **API** (via the `yfinance` wrapper library).
    * *Note:* We do not use manual regex scraping. We utilize the `yfinance` API to fetch structured DataFrames for tickers (e.g., AAPL, BTC-USD, GLD).

### **Tech Stack**
* **Frontend:** Streamlit (Python-based web framework).
* **Data Processing:** Pandas & NumPy (Vectorized operations).
* **Visualization:**
    * *Matplotlib* (Quant A: Static, publication-quality technical charts).
    * *Plotly* (Quant B: Interactive, zoomable portfolio comparisons).
* **Automation:** Linux Cron Jobs & Shell Scripting.

### **Directory Structure**
```text
project-dashboard/
│
├── app/
│   ├── main.py                 # 🎛️ CONTROLLER: Routes traffic to Module A or B
│   ├── dashboard_a.py          # 📈 QUANT A: Single-asset logic & Matplotlib charts
│   └── quant_b_module/         # 💰 QUANT B: Portfolio logic package
│       ├── dashboard_b.py      #    - Frontend: Plotly visualization & Auto-refresh
│       ├── portfolio_manager.py#    - Core Logic: Backtesting engine & Math formulas
│       ├── data_manager.py     #    - Data Layer: API fetching, Caching, Cleaning
│       └── daily_report.py     #    - Backend: Standalone script for cron jobs
│
├── data_reports/               # 📂 OUTPUT: Local storage for generated risk reports
├── setup_cron.sh               # ⚙️ DEVOPS: Automated script to configure Linux Cron
├── requirements.txt            # 📦 DEPENDENCIES: Python libraries
└── README.md                   # 📄 DOCS: Project documentation
