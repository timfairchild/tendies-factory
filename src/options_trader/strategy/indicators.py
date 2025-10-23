import numpy as np
import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up, index=series.index).ewm(alpha=1/period, adjust=False).mean()
    roll_down = pd.Series(down, index=series.index).ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    return 100 - (100 / (1 + rs))

def vwap(df: pd.DataFrame) -> pd.Series:
    # df requires columns: ['Open','High','Low','Close','Volume']
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3.0
    cum_tp_vol = (typical_price * df['Volume']).cumsum()
    cum_vol = (df['Volume']).cumsum().replace(0, np.nan)
    return cum_tp_vol / cum_vol
