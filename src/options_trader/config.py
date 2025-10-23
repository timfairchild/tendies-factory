from pydantic import BaseModel
import os

def getenv_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except Exception:
        return default

def getenv_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except Exception:
        return default

class Settings(BaseModel):
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "SPY")
    default_iv: float = getenv_float("DEFAULT_IV", 0.25)
    default_dte: int = getenv_int("DEFAULT_DTE", 5)
    default_target_delta: float = getenv_float("DEFAULT_TARGET_DELTA", 0.35)
    default_tp_pct: float = getenv_float("DEFAULT_TP_PCT", 0.20)
    default_sl_pct: float = getenv_float("DEFAULT_SL_PCT", 0.30)
    default_max_contracts: int = getenv_int("DEFAULT_MAX_CONTRACTS", 1)

settings = Settings()
