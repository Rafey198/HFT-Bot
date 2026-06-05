"""Market regime detection using ADX, ATR percentile, MA slope, BB bandwidth."""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from ..features.pipeline import build_features

REGIME_STRATEGY_MAP = {
    "trending_bullish": (["trend", "momentum"], ["volatility"]),
    "trending_bearish": (["trend", "momentum"], ["volatility"]),
    "ranging": (["volatility", "momentum"], ["trend", "session"]),
    "high_volatility": (["volatility", "session"], ["momentum"]),
    "low_volatility": (["volatility", "trend"], ["session"]),
    "news_like_spike": ([], ["trend", "momentum", "volatility", "session"]),
    "choppy_avoid": ([], ["trend", "momentum", "volatility", "session", "price_action"]),
}


def detect_regime(df: pd.DataFrame, lookback: int = 1) -> Dict:
    """Detect the regime at the most recent bar."""
    if not {"adx", "atr", "bb_bandwidth", "ema_50"}.issubset(df.columns):
        df, _ = build_features(df, drop_na=False)
    df = df.dropna(subset=["adx", "atr", "ema_50"]).reset_index(drop=True)
    if len(df) < 60:
        return {
            "regime": "ranging", "confidence": 30,
            "recommended_strategy_types": ["volatility"],
            "avoid_strategy_types": ["trend"],
            "reason": "Not enough data to classify reliably.",
        }

    i = len(df) - 1
    adx = float(df["adx"].iloc[i])
    atr = df["atr"]
    atr_pct = float(atr.rolling(200, min_periods=30).rank(pct=True).iloc[i])
    ema50 = df["ema_50"]
    slope = float((ema50.iloc[i] - ema50.iloc[max(0, i - 20)]) / (abs(ema50.iloc[max(0, i - 20)]) + 1e-9))
    bandwidth = float(df["bb_bandwidth"].iloc[i])
    recent_range = float((df["high"].iloc[i - 10:i + 1].max() - df["low"].iloc[i - 10:i + 1].min())
                         / (df["close"].iloc[i] + 1e-9))
    atr_now = float(atr.iloc[i])
    atr_mean = float(atr.iloc[max(0, i - 50):i + 1].mean())
    spike = atr_now > atr_mean * 2.2

    reason_parts = [f"ADX={adx:.0f}", f"ATR pct={atr_pct:.2f}", f"slope={slope:+.4f}"]

    if spike:
        regime = "news_like_spike"
        confidence = 80
    elif adx < 18 and atr_pct > 0.4 and abs(slope) < 0.001 and bandwidth > recent_range * 0.5:
        regime = "choppy_avoid"
        confidence = 60
    elif adx >= 25 and slope > 0.0008:
        regime = "trending_bullish"
        confidence = min(95, 50 + adx)
    elif adx >= 25 and slope < -0.0008:
        regime = "trending_bearish"
        confidence = min(95, 50 + adx)
    elif atr_pct > 0.8:
        regime = "high_volatility"
        confidence = 70
    elif atr_pct < 0.25:
        regime = "low_volatility"
        confidence = 65
    else:
        regime = "ranging"
        confidence = 55

    rec, avoid = REGIME_STRATEGY_MAP.get(regime, ([], []))
    return {
        "regime": regime,
        "confidence": round(float(confidence), 1),
        "recommended_strategy_types": rec,
        "avoid_strategy_types": avoid,
        "reason": ", ".join(reason_parts) + f" → {regime.replace('_', ' ')}",
    }
