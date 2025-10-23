import numpy as np
import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    # Ensure 1D series
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    series = pd.Series(series, copy=False).astype(float).squeeze()

    delta = series.diff()

    # Use pandas ops to keep alignment and avoid shape issues
    gains = delta.clip(lower=0.0)
    losses = (-delta).clip(lower=0.0)

    roll_up = gains.ewm(alpha=1/period, adjust=False).mean()
    roll_down = losses.ewm(alpha=1/period, adjust=False).mean()

    # Avoid divide-by-zero
    denom = roll_down.replace(0.0, 1e-12)
    rs = roll_up / denom
    return 100 - (100 / (1 + rs))

def vwap(df: pd.DataFrame) -> pd.Series:
    # df requires columns: ['Open','High','Low','Close','Volume']
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3.0
    cum_tp_vol = (typical_price * df['Volume']).cumsum()
    cum_vol = (df['Volume']).cumsum().replace(0, np.nan)
    return cum_tp_vol / cum_vol