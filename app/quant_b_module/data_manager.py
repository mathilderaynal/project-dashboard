import yfinance as yf
import pandas as pd

class PortfolioDataManager:
    def __init__(self, tickers):
        """
        Initializes the Data Manager with a list of asset tickers.
        Example: tickers = ['AAPL', 'GOOGL', 'BTC-USD']
        """
        self.tickers = tickers

    def fetch_live_data(self, period="1d", interval="5m"):
        """
        Fetches historical data for the initialized tickers.
        
        Args:
            period (str): The time period to download.
            interval (str): The frequency of data. Project requires ~5 mins.
        
        Returns:
            pd.DataFrame: A clean DataFrame containing only the 'Close' prices.
        """
        print(f"Fetching data for: {self.tickers}...")
        
        # yfinance allows downloading multiple tickers at once.
        # threads=True speeds up the download.
        data = yf.download(
            tickers=self.tickers, 
            period=period, 
            interval=interval, 
            group_by='ticker',
            auto_adjust=True,
            threads=True
        )
        
        # Structure the data so we just have a table of Close prices
        clean_df = pd.DataFrame()
        
        for ticker in self.tickers:
            # Check if the ticker data was actually retrieved
            if ticker in data:
                # We target the 'Close' column for our portfolio calculations
                clean_df[ticker] = data[ticker]['Close']
        
        # Remove rows where data might be missing (common in live fetching)
        clean_df.dropna(how='all', inplace=True)
        
        return clean_df

# --- TEST BLOCK ---
# This runs only when you execute this file directly
if __name__ == "__main__":
    # We use 3 distinct assets as required: A Stock, Crypto, and Gold ETF
    test_tickers = ['AAPL', 'BTC-USD', 'GLD']
    manager = PortfolioDataManager(test_tickers)
    
    df = manager.fetch_live_data()
    
    print("\n--- SUCCESS: Data Retrieved ---")
    print(df.tail())
    print("\n--- Data Info ---")
    print(df.info())
