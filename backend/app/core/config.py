"""Central configuration for AurumFX backend."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
DATA_DIR = BASE_DIR / "storage"
DATA_DIR.mkdir(exist_ok=True, parents=True)

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

CLEAN_DIR = DATA_DIR / "clean"
CLEAN_DIR.mkdir(exist_ok=True, parents=True)

REPORT_DIR = DATA_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True, parents=True)

DB_PATH = DATA_DIR / "aurumfx.db"

DISCLAIMER = (
    "This system is for research, backtesting, and educational purposes. "
    "Forex and gold trading are high risk. Past performance does not guarantee "
    "future results. This system can lose money. Always use paper trading before "
    "live execution."
)

LIVE_CONFIRMATION_PHRASE = "I understand this can lose money"

# Supported instruments. Pip/point sizes used for spread + sizing math.
SUPPORTED_SYMBOLS: List[str] = [
    "XAUUSD",
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "USDCHF",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
]

PRIMARY_SYMBOL = "XAUUSD"

SUPPORTED_TIMEFRAMES: List[str] = ["tick", "M1", "M5", "M15", "M30", "H1", "H4", "D1"]

# Approximate starting price + point value used for synthetic data + sizing.
SYMBOL_SPECS: Dict[str, Dict[str, float]] = {
    "XAUUSD": {"price": 2350.0, "point": 0.01, "pip": 0.1, "spread_points": 20, "vol": 0.0009},
    "EURUSD": {"price": 1.0850, "point": 0.00001, "pip": 0.0001, "spread_points": 8, "vol": 0.0004},
    "GBPUSD": {"price": 1.2700, "point": 0.00001, "pip": 0.0001, "spread_points": 10, "vol": 0.0005},
    "USDJPY": {"price": 157.50, "point": 0.001, "pip": 0.01, "spread_points": 9, "vol": 0.0004},
    "USDCHF": {"price": 0.9050, "point": 0.00001, "pip": 0.0001, "spread_points": 10, "vol": 0.0004},
    "AUDUSD": {"price": 0.6650, "point": 0.00001, "pip": 0.0001, "spread_points": 9, "vol": 0.0005},
    "USDCAD": {"price": 1.3680, "point": 0.00001, "pip": 0.0001, "spread_points": 10, "vol": 0.0004},
    "NZDUSD": {"price": 0.6100, "point": 0.00001, "pip": 0.0001, "spread_points": 11, "vol": 0.0005},
}

TIMEFRAME_MINUTES: Dict[str, int] = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 60,
    "H4": 240,
    "D1": 1440,
}

DEFAULT_RISK_SETTINGS: Dict[str, float] = {
    "initial_balance": 10000,
    "risk_per_trade": 0.25,
    "max_daily_loss": 2.0,
    "max_weekly_loss": 5.0,
    "max_drawdown_stop": 10.0,
    "max_trades_per_minute": 5,
    "max_trades_per_day": 50,
    "max_consecutive_losses": 3,
    "max_open_positions": 2,
    "min_reward_risk": 1.2,
    "max_spread_points": 30,
    "min_signal_confidence": 60,
}


def symbol_spec(symbol: str) -> Dict[str, float]:
    return SYMBOL_SPECS.get(symbol.upper(), SYMBOL_SPECS[PRIMARY_SYMBOL])


CORS_ORIGINS = os.environ.get(
    "AURUMFX_CORS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")
