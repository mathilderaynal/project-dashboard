import pandas as pd
import numpy as np

class PortfolioSimulator:
    def __init__(self, data):
        # Robust data cleaning: Forward fill first, then Back fill to handle gaps
        self.data = data.ffill().bfill().dropna()
        self.returns = self.data.pct_change().dropna()
        self.cumulative_return = None

    def simulate_portfolio(self, weights, rebalance=True):
        """
        rebalance=True: Constant Weights (Continuous Rebalancing)
        rebalance=False: Buy and Hold (Drifting Weights)
        """
        if rebalance:
            # METHOD 1: Constant Rebalancing (Fixed Weights)
            weight_list = [weights[col] for col in self.data.columns]
            weighted_returns = self.returns.dot(weight_list)
            self.cumulative_return = (1 + weighted_returns).cumprod() * 100
        else:
            # METHOD 2: Buy & Hold (Weights Drift)
            # We normalize prices to 100 at start and allocate capital
            normalized_prices = self.data / self.data.iloc[0]
            
            # Create a dataframe where each column is the value of that asset in the portfolio
            weighted_curves = pd.DataFrame()
            for ticker, weight in weights.items():
                weighted_curves[ticker] = normalized_prices[ticker] * weight * 100
            
            # Portfolio value is the sum of the parts
            self.cumulative_return = weighted_curves.sum(axis=1)

        # Align indices
        self.cumulative_return.index = self.data.index[len(self.data)-len(self.cumulative_return):]
        return self.cumulative_return

    def get_metrics(self):
        if self.cumulative_return is None:
            return {}
        
        # Calculate returns of the portfolio curve itself
        port_returns = self.cumulative_return.pct_change().dropna()
        
        metrics = {
            # Annualize volatility (approximate for intraday/daily)
            'volatility': port_returns.std() * np.sqrt(252 * 24 * 4), 
            'total_return': (self.cumulative_return.iloc[-1] / self.cumulative_return.iloc[0]) - 1,
            'correlation': self.data.corr()
        }
        return metrics
