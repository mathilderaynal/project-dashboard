import pandas as pd
import numpy as np

class PortfolioSimulator:
    def __init__(self, data):
        """
        Initializes with the dataframe of asset prices.
        data: pd.DataFrame with datetime index and columns = asset names
        """
        # Forward fill missing data (e.g., if Stock market is closed but Crypto isn't)
        self.data = data.ffill().dropna()
        self.returns = self.data.pct_change().dropna()
    
    def simulate_portfolio(self, weights):
        """
        Simulates portfolio performance based on given weights.
        
        Args:
            weights (dict): dictionary of {ticker: weight}, e.g., {'AAPL': 0.5, 'BTC-USD': 0.5}
            
        Returns:
            pd.Series: The cumulative return series of the portfolio (for plotting)
        """
        # 1. Align weights with the data columns order
        weight_list = [weights.get(col, 0) for col in self.returns.columns]
        
        # 2. Normalize weights to ensure they sum to 1 (100%)
        total_weight = sum(weight_list)
        if total_weight == 0:
            weight_list = [1.0/len(weight_list)] * len(weight_list) # Default to equal weight
        else:
            weight_list = [w / total_weight for w in weight_list]
            
        # 3. Calculate Weighted Returns: Sum(Weight * Asset_Return)
        # dot product is efficient for this: Returns_Matrix • Weights_Vector
        portfolio_daily_returns = self.returns.dot(weight_list)
        
        # 4. Calculate Cumulative Return: (1 + r1) * (1 + r2) * ...
        portfolio_cumulative_return = (1 + portfolio_daily_returns).cumprod()
        
        # Start at 1.0 (base 100) for better visualization
        portfolio_cumulative_return = 100 * portfolio_cumulative_return
        
        return portfolio_cumulative_return

    def get_metrics(self):
        """
        Calculates required risk/return metrics.
        Returns:
            dict: Volatility and Correlation Matrix
        """
        # Correlation Matrix (Project Requirement)
        correlation_matrix = self.returns.corr()
        
        # Volatility (Annualized) - assuming 252 trading days roughly, 
        # or for 5-min data we might look at simple stdev
        volatility = self.returns.std() * np.sqrt(252) 
        
        return {
            "correlation": correlation_matrix,
            "volatility": volatility
        }

# --- TEST BLOCK ---
if __name__ == "__main__":
    # 1. Simulate getting data (using the DataManager we built before)
    from data_manager import PortfolioDataManager
    
    tickers = ['AAPL', 'BTC-USD', 'GLD']
    # Fetch 5 days of data to ensure we have enough points for math
    raw_data = PortfolioDataManager(tickers).fetch_live_data(period="5d", interval="15m")
    
    # 2. Initialize Simulator
    sim = PortfolioSimulator(raw_data)
    
    # 3. Define Test Weights (50% Bitcoin, 25% Apple, 25% Gold)
    my_weights = {'BTC-USD': 0.5, 'AAPL': 0.25, 'GLD': 0.25}
    
    # 4. Run Simulation
    port_curve = sim.simulate_portfolio(my_weights)
    metrics = sim.get_metrics()
    
    print("\n--- Portfolio Cumulative Value (Last 5 points) ---")
    print(port_curve.tail())
    
    print("\n--- Correlation Matrix ---")
    print(metrics['correlation'])
