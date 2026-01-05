import pandas as pd
import yfinance as yf


def fetch_price_history(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Download historical price data for a given symbol.

    Parameters
    ----------
    symbol : str
        Example: 'BTC-USD', 'EURUSD=X', 'AAPL'
    period : str
        Example: '1mo', '3mo', '6mo', '1y'
    interval : str
        Example: '1d', '1h'

    Returns
    -------
    pd.DataFrame
        OHLCV dataframe with columns like Open, High, Low, Close, Volume
    """
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    df = df.dropna()

    # Ensure we have a standard 'Close' column (yfinance sometimes returns multi-index)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    return df
