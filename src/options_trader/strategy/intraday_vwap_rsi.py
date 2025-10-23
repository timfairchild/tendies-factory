from dataclasses import dataclass
import pandas as pd
from .indicators import rsi, vwap

@dataclass
class SignalConfig:
    rsi_period: int = 14
    rsi_midline: float = 50.0

@dataclass
class SignalState:
    prev_rsi: float | None = None

class VWAPRSIStrategy:
    def __init__(self, cfg: SignalConfig | None = None):
        self.cfg = cfg or SignalConfig()
        self.state = SignalState()

    def compute(self, df: pd.DataFrame) -> pd.Series:
        """
        Returns a pandas Series of signals aligned to df index:
        'buy_call', 'buy_put', or 'hold'
        """
        df = df.copy()
        df['VWAP'] = vwap(df)
        df['RSI'] = rsi(df['Close'], period=self.cfg.rsi_period)

        signals = []
        for _, row in df.iterrows():
            price = row['Close']
            vw = row['VWAP']
            r = row['RSI']
            prev_r = self.state.prev_rsi

            sig = 'hold'
            if price > vw and prev_r is not None and prev_r < self.cfg.rsi_midline and r >= self.cfg.rsi_midline:
                sig = 'buy_call'
            elif price < vw and prev_r is not None and prev_r > self.cfg.rsi_midline and r <= self.cfg.rsi_midline:
                sig = 'buy_put'

            signals.append(sig)
            self.state.prev_rsi = r

        return pd.Series(signals, index=df.index, name='signal')
