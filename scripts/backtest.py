import argparse
import os
from datetime import time
import pandas as pd
import yfinance as yf
from loguru import logger
from options_trader.engine.backtest import BacktestEngine, RiskConfig
from options_trader.options.selector import SelectionConfig
from options_trader.config import settings

def load_intraday(symbol: str, start_days_ago: int = 5) -> pd.DataFrame:
    period = f"{max(1, start_days_ago)}d"
    df = yf.download(symbol, interval="1m", period=period, auto_adjust=False, progress=False)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    df = df.tz_localize(None)
    # Filter regular market hours 09:30 to 16:00
    market_open = time(9, 30)
    market_close = time(16, 0)
    df = df[df.index.map(lambda x: market_open <= x.time() <= market_close)]
    df = df.rename(columns={"Open":"Open","High":"High","Low":"Low","Close":"Close","Volume":"Volume"})
    df = df[["Open","High","Low","Close","Volume"]].dropna()
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default=settings.default_symbol)
    parser.add_argument("--iv", type=float, default=settings.default_iv)
    parser.add_argument("--dte", type=int, default=settings.default_dte)
    parser.add_argument("--target-delta", type=float, default=settings.default_target_delta)
    parser.add_argument("--tp", type=float, default=settings.default_tp_pct)
    parser.add_argument("--sl", type=float, default=settings.default_sl_pct)
    parser.add_argument("--max-contracts", type=int, default=settings.default_max_contracts)
    parser.add_argument("--start-days-ago", type=int, default=5)
    args = parser.parse_args()

    logger.remove()
    logger.add(lambda m: print(m, end=""), level=os.getenv("LOG_LEVEL", settings.log_level))

    df = load_intraday(args.symbol, start_days_ago=args.start_days_ago)
    if df.empty:
        logger.error("No data loaded. Try a different symbol or a longer period.")
        return

    sel_cfg = SelectionConfig(target_delta=args.target_delta, dte=args.dte, iv=args.iv)
    risk_cfg = RiskConfig(max_contracts=args.max_contracts, tp_pct=args.tp, sl_pct=args.sl)

    engine = BacktestEngine(symbol=args.symbol, selection_cfg=sel_cfg, risk_cfg=risk_cfg)
    pnl = engine.run(df)
    print(f"\nSummary: symbol={args.symbol} DTE={args.dte} target_delta={args.target_delta} "
          f"IV={args.iv} TP={args.tp} SL={args.sl} -> Realized PnL: {pnl:+.2f}")

if __name__ == "__main__":
    main()
