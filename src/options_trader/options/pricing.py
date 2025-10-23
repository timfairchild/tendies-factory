import math

SQRT_2PI = math.sqrt(2 * math.pi)

def _phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_2PI

def _Phi(x: float) -> float:
    # Standard normal CDF via erf
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def black_scholes_price(S: float, K: float, T: float, sigma: float, option_type: str, r: float = 0.0) -> float:
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return max(0.0, S - K) if option_type == 'call' else max(0.0, K - S)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == 'call':
        return S * _Phi(d1) - K * math.exp(-r * T) * _Phi(d2)
    else:
        return K * math.exp(-r * T) * _Phi(-d2) - S * _Phi(-d1)

def black_scholes_delta(S: float, K: float, T: float, sigma: float, option_type: str, r: float = 0.0) -> float:
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        if option_type == 'call':
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    if option_type == 'call':
        return _Phi(d1)
    else:
        return _Phi(d1) - 1.0
