from dataclasses import dataclass
from typing import Literal
import numpy as np
from .pricing import black_scholes_price, black_scholes_delta

@dataclass
class SelectionConfig:
    target_delta: float = 0.35  # + for calls, - for puts
    dte: int = 5
    iv: float = 0.25
    strike_step: float = 1.0  # $1 strikes typical on SPY/QQQ
    r: float = 0.0

@dataclass
class OptionSelection:
    option_type: Literal['call','put']
    strike: float
    dte: int
    delta: float
    premium_est: float

def select_contract(S: float, direction: Literal['call','put'], cfg: SelectionConfig) -> OptionSelection:
    T = max(cfg.dte, 1) / 252.0
    # Build a reasonable strike grid around spot
    base = int(round(S / cfg.strike_step)) * cfg.strike_step
    strikes = np.array([base + i * cfg.strike_step for i in range(-15, 16)], dtype=float)

    target = cfg.target_delta if direction == 'call' else -cfg.target_delta
    best = None
    best_err = float('inf')

    for K in strikes:
        delta = black_scholes_delta(S, K, T, cfg.iv, direction, cfg.r)
        err = abs(delta - target)
        if err < best_err:
            prem = black_scholes_price(S, K, T, cfg.iv, direction, cfg.r)
            best = OptionSelection(direction, float(K), cfg.dte, float(delta), float(prem))
            best_err = err

    if best is None:
        # Fallback ATM
        K = base
        return OptionSelection(direction, float(K), cfg.dte,
                               float(black_scholes_delta(S, K, T, cfg.iv, direction, cfg.r)),
                               float(black_scholes_price(S, K, T, cfg.iv, direction, cfg.r)))
    return best
