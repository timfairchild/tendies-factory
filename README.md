# Tendies Factory — Options Algo Starter

Intraday options trading scaffold focused on "longer intraday swing" setups with the ability to experiment with shorter scalps.

This starter provides:
- A research/backtest loop using minute bars of the underlying (from yfinance)
- A VWAP + RSI setup that goes long calls in bullish regimes and long puts in bearish regimes
- Option contract selection by target delta and DTE using Black–Scholes pricing
- A simple paper simulation engine and PnL accounting
- Clean seams to plug in a live broker adapter (Interactive Brokers, Tradier, Tastytrade, etc.)

Important: Fidelity does not offer a retail trading API as of 2025; use a broker with an API for live execution.

## Quick start

1) Install dependencies (Python 3.11+):
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

2) Copy `.env.example` to `.env` and adjust if needed.

3) Run a quick backtest on SPY:
```
python scripts/backtest.py --symbol SPY --dte 5 --target-delta 0.35 --start-days-ago 5
```

You’ll see logs of entries/exits and a summary PnL.

## Strategy (initial)

- Signal: 
  - Bullish: Price above VWAP; RSI(14) crosses up through 50 → Buy call
  - Bearish: Price below VWAP; RSI(14) crosses down through 50 → Buy put
- Risk:
  - One contract per entry by default
  - 30% stop-loss, 20% take-profit on the option premium (configurable)
- Contract selection:
  - Pick DTE N (e.g., 5 trading days)
  - Choose strike whose BS delta is closest to target (e.g., 0.35 for calls, -0.35 for puts)
  - Simple spread/liquidity checks can be added when you integrate real chain/quotes

Note: For backtests, option premiums are estimated via Black–Scholes with a configurable implied volatility assumption (default 0.25) and zero rates. Replace with vendor/broker greeks for more realism.

## Next steps

- Choose a live broker:
  - IBKR: Most flexible, robust portfolio and order types
  - Tradier: Simple REST API, sandbox, convenient options endpoints
  - Tastytrade: Popular among options traders; API access available for approved accounts
- Add a real data vendor for options chains and quotes (Polygon.io is a common choice)
- Implement broker adapter in `src/options_trader/brokers/` and wire to a live runner
- Enhance backtesting:
  - Use actual option chain mid prices instead of BS estimates
  - Slippage/commissions modeling per-broker
  - Market regime filters and spread/liquidity filters

## Disclaimer

This project is for educational and engineering purposes only and is not financial advice. Trading involves substantial risk. Confirm your broker’s terms and all regulations before automating live orders.