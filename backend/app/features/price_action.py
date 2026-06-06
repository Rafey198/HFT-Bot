"""Price-action features: candle anatomy, patterns, structure, S/R zones."""
from __future__ import annotations

import numpy as np
import pandas as pd


def add_price_action(df: pd.DataFrame, swing_lookback: int = 5) -> pd.DataFrame:
    out = df.copy()
    o, h, l, c = out["open"], out["high"], out["low"], out["close"]

    out["body"] = (c - o).abs()
    out["range"] = (h - l).replace(0, np.nan)
    out["upper_wick"] = h - np.maximum(o, c)
    out["lower_wick"] = np.minimum(o, c) - l
    out["body_pct"] = (out["body"] / out["range"]).fillna(0)
    out["bullish"] = (c > o).astype(int)

    prev_o, prev_c = o.shift(1), c.shift(1)
    out["bull_engulf"] = (
        (c > o) & (prev_c < prev_o) & (c >= prev_o) & (o <= prev_c)
    ).astype(int)
    out["bear_engulf"] = (
        (c < o) & (prev_c > prev_o) & (o >= prev_c) & (c <= prev_o)
    ).astype(int)

    rng = out["range"].fillna(0)
    out["pin_bar_bull"] = ((out["lower_wick"] > 2 * out["body"]) &
                           (out["upper_wick"] < out["body"]) & (rng > 0)).astype(int)
    out["pin_bar_bear"] = ((out["upper_wick"] > 2 * out["body"]) &
                           (out["lower_wick"] < out["body"]) & (rng > 0)).astype(int)

    out["inside_bar"] = ((h < h.shift(1)) & (l > l.shift(1))).astype(int)

    win = swing_lookback
    out["swing_high"] = ((h == h.rolling(2 * win + 1, center=True).max())).astype(int)
    out["swing_low"] = ((l == l.rolling(2 * win + 1, center=True).min())).astype(int)

    recent_high = h.rolling(20).max()
    recent_low = l.rolling(20).min()
    out["break_of_structure_up"] = (c > recent_high.shift(1)).astype(int)
    out["break_of_structure_down"] = (c < recent_low.shift(1)).astype(int)

    out["resistance"] = recent_high
    out["support"] = recent_low
    return out
