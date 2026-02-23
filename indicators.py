import pandas as pd


def add_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    if "close" not in df.columns:
        raise ValueError("Column 'close' not found in DataFrame")

    df[f"SMA_{window}"] = df["close"].rolling(window=window).mean()
    return df


def add_ema(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    if "close" not in df.columns:
        raise ValueError("Column 'close' not found in DataFrame")

    df[f"EMA_{window}"] = df["close"].ewm(span=window, adjust=False).mean()
    return df


def add_indicators(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    df = add_sma(df, window)
    df = add_ema(df, window)
    return df