import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")

        return df

    except Exception as e:
        raise RuntimeError(f"Error fetching data for {symbol}: {str(e)}")