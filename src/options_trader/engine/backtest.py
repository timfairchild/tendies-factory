from dataclasses import dataclass
from typing import Literal
import pandas as pd
from loguru import logger
from ..strategy.intraday_vwap_rsi import VWAPRSIStrategy, SignalConfig
from ..options.selector import select_contract, SelectionConfig, OptionSelection

@dataclass
class RiskConfig:
    max_contracts: int = 1
    tp_pct: float = 0.20
    sl_pct: float = 0.30
    commission_per_contract: float = 0.65

@dataclass
class Position:
    side: Literal['long_call','long_put']
    contract: OptionSelection
    qty: int
    entry_price: float  # option price
    entry_value: float  # entry_price * qty * 100
    entry_time: pd.Timestamp

class BacktestEngine:
    def __init__(self,
                 symbol: str,
                 selection_cfg: SelectionConfig,
                 risk_cfg: RiskConfig,
                 signal_cfg: SignalConfig | None = None):
        self.symbol = symbol
        self.selection_cfg = selection_cfg
        self.risk_cfg = risk_cfg
        self.strategy = VWAPRSIStrategy(signal_cfg)
        self.position: Position | None = None
        self.realized_pnl: float = 0.0

    def _option_mark(self, contract: OptionSelection, spot: float) -> float:
        # Recompute premium estimate at current spot with same DTE and IV
        sc = self.selection_cfg
        T = max(sc.dte, 1) / 252.0
        from ..options.pricing import black_scholes_price
        return float(black_scholes_price(spot, contract.strike, T, sc.iv, contract.option_type, sc.r))

    def _enter(self, when: pd.Timestamp, side: Literal['long_call','long_put'], spot: float):
        if self.position is not None:
            return
        direction = 'call' if side == 'long_call' else 'put'
        contract = select_contract(spot, direction, self.selection_cfg)
        mark = self._option_mark(contract, spot)
        qty = max(1, min(self.risk_cfg.max_contracts, 10))
        entry_value = mark * qty * 100 + self.risk_cfg.commission_per_contract * qty
        self.position = Position(side=side, contract=contract, qty=qty,
                                 entry_price=mark, entry_value=entry_value, entry_time=when)
        logger.info(f"ENTER {side.upper()} {self.symbol} {qty} @ {mark:.2f} "
                    f"strike {contract.strike} Δ {contract.delta:.2f} DTE {contract.dte} at {when}")

    def _exit(self, when: pd.Timestamp, spot: float, reason: str):
        if self.position is None:
            return
        current_mark = self._option_mark(self.position.contract, spot)
        exit_value = current_mark * self.position.qty * 100 - self.risk_cfg.commission_per_contract * self.position.qty
        pnl = exit_value - self.position.entry_value
        self.realized_pnl += pnl
        logger.info(f"EXIT  {self.position.side.upper()} {self.symbol} {self.position.qty} @ {current_mark:.2f} "
                    f"PnL {pnl:+.2f} ({reason}) at {when}")
        self.position = None

    def run(self, df: pd.DataFrame):
        """
        df: minute bars with columns Open, High, Low, Close, Volume and DatetimeIndex
        """
        signals = self.strategy.compute(df)
        df = df.copy()
        df['signal'] = signals

        for ts, row in df.iterrows():
            spot = float(row['Close'])
            sig = row['signal']

            # Manage exits
            if self.position is not None:
                mark = self._option_mark(self.position.contract, spot)
                change = (mark - self.position.entry_price) / max(1e-9, self.position.entry_price)
                if change >= self.risk_cfg.tp_pct:
                    self._exit(ts, spot, reason=f"TP {change:.0%}")
                elif change <= -self.risk_cfg.sl_pct:
                    self._exit(ts, spot, reason=f"SL {change:.0%}")
                else:
                    # Direction flip: cross VWAP the other way
                    if self.position.side == 'long_call' and sig == 'buy_put':
                        self._exit(ts, spot, reason="flip to put")
                    elif self.position.side == 'long_put' and sig == 'buy_call':
                        self._exit(ts, spot, reason="flip to call")

            # Manage entries
            if self.position is None:
                if sig == 'buy_call':
                    self._enter(ts, 'long_call', spot)
                elif sig == 'buy_put':
                    self._enter(ts, 'long_put', spot)

        # Close any open at session end
        if self.position is not None:
            last_ts = df.index[-1]
            last_spot = float(df.iloc[-1]['Close'])
            self._exit(last_ts, last_spot, reason="session end")

        logger.info(f"TOTAL REALIZED PnL: {self.realized_pnl:+.2f}")
        return self.realized_pnl
