"""Full feature-engineering pipeline + report."""
from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from .indicators import add_indicators
from .price_action import add_price_action
from .sessions import add_sessions

FEATURE_LIST = [
    "sma", "ema", "wma", "macd", "adx", "supertrend", "ichimoku",
    "rsi", "stochastic", "cci", "roc", "williams_r",
    "atr", "bollinger_bands", "keltner_channels", "donchian_channels", "bb_bandwidth",
    "obv", "volume_ma", "vwap",
    "candle_body", "upper_wick", "lower_wick", "range", "engulfing", "pin_bar",
    "inside_bar", "swing_high", "swing_low", "break_of_structure", "support_resistance",
    "london_session", "ny_session", "asian_session", "london_ny_overlap",
    "hour_of_day", "day_of_week",
]


def build_features(df: pd.DataFrame, drop_na: bool = True) -> Tuple[pd.DataFrame, Dict]:
    warnings = []
    if "volume" not in df.columns:
        df = df.copy()
        df["volume"] = 0
        warnings.append("Volume column missing — VWAP/OBV may be unreliable.")

    out = add_indicators(df)
    out = add_price_action(out)
    out = add_sessions(out)

    before = len(out)
    if drop_na:
        # Keep core columns; drop early warm-up rows where long EMAs are NaN.
        out = out.dropna(subset=["ema_200", "atr", "rsi"]).reset_index(drop=True)
    nan_removed = before - len(out)

    report = {
        "features_created": FEATURE_LIST,
        "rows_after_feature_engineering": len(out),
        "nan_rows_removed": nan_removed,
        "warnings": warnings,
    }
    return out, report
