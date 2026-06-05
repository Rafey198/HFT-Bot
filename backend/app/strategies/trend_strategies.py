"""Trend-following strategies."""
from __future__ import annotations

import pandas as pd

from .base import Strategy, cross_down, cross_up, to_dir


class SmaCrossover(Strategy):
    key = "sma_crossover"
    name = "SMA Crossover"
    category = "trend"
    description = "Fast SMA crossing a slow SMA signals trend direction."
    default_params = {"fast": 20, "slow": 50}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast = df["close"].rolling(self.params["fast"], min_periods=1).mean()
        slow = df["close"].rolling(self.params["slow"], min_periods=1).mean()
        return to_dir(cross_up(fast, slow), cross_down(fast, slow))


class EmaCrossover(Strategy):
    key = "ema_crossover"
    name = "EMA Crossover"
    category = "trend"
    description = "Fast EMA crossing slow EMA — reacts faster than SMA."
    default_params = {"fast": 9, "slow": 21}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast = df["close"].ewm(span=self.params["fast"], adjust=False).mean()
        slow = df["close"].ewm(span=self.params["slow"], adjust=False).mean()
        return to_dir(cross_up(fast, slow), cross_down(fast, slow))


class TripleEmaTrend(Strategy):
    key = "triple_ema_trend"
    name = "Triple EMA Trend"
    category = "trend"
    description = "EMA 9/21/50 stacked alignment confirms strong trend."
    default_params = {"fast": 9, "mid": 21, "slow": 50}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        f = df["close"].ewm(span=self.params["fast"], adjust=False).mean()
        m = df["close"].ewm(span=self.params["mid"], adjust=False).mean()
        s = df["close"].ewm(span=self.params["slow"], adjust=False).mean()
        up = (f > m) & (m > s)
        dn = (f < m) & (m < s)
        return to_dir(up & ~up.shift(1).fillna(False), dn & ~dn.shift(1).fillna(False))


class MacdCrossover(Strategy):
    key = "macd_crossover"
    name = "MACD Crossover"
    category = "trend"
    description = "MACD line crossing the signal line."
    default_params = {}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return to_dir(cross_up(df["macd"], df["macd_signal"]),
                      cross_down(df["macd"], df["macd_signal"]))


class SupertrendFollowing(Strategy):
    key = "supertrend_following"
    name = "Supertrend Following"
    category = "trend"
    description = "Follow the Supertrend direction flips."
    sl_atr = 1.2
    tp_atr = 3.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        d = df["supertrend_dir"]
        return to_dir((d > 0) & (d.shift(1) <= 0), (d < 0) & (d.shift(1) >= 0))


class AdxTrendStrength(Strategy):
    key = "adx_trend_strength"
    name = "ADX Trend Strength"
    category = "trend"
    description = "Trade DI crossovers only when ADX confirms strong trend."
    default_params = {"adx_min": 25}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        strong = df["adx"] > self.params["adx_min"]
        up = cross_up(df["plus_di"], df["minus_di"]) & strong
        dn = cross_down(df["plus_di"], df["minus_di"]) & strong
        return to_dir(up, dn)


class IchimokuCloudTrend(Strategy):
    key = "ichimoku_cloud_trend"
    name = "Ichimoku Cloud Trend"
    category = "trend"
    description = "Price relative to cloud + tenkan/kijun cross."
    sl_atr = 1.5
    tp_atr = 3.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        above = (df["close"] > df["ichimoku_span_a"]) & (df["close"] > df["ichimoku_span_b"])
        below = (df["close"] < df["ichimoku_span_a"]) & (df["close"] < df["ichimoku_span_b"])
        up = cross_up(df["ichimoku_tenkan"], df["ichimoku_kijun"]) & above
        dn = cross_down(df["ichimoku_tenkan"], df["ichimoku_kijun"]) & below
        return to_dir(up, dn)


class AtrTrailingTrend(Strategy):
    key = "atr_trailing_trend"
    name = "ATR Trailing Stop Trend"
    category = "trend"
    description = "EMA trend bias with ATR-based trailing exits."
    sl_atr = 2.0
    tp_atr = 4.0
    default_params = {"ema": 50}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ema = df["close"].ewm(span=self.params["ema"], adjust=False).mean()
        up = cross_up(df["close"], ema)
        dn = cross_down(df["close"], ema)
        return to_dir(up, dn)


class MomentumContinuation(Strategy):
    key = "momentum_continuation"
    name = "Momentum Continuation"
    category = "trend"
    description = "Buy strong ROC momentum in the direction of the trend."
    default_params = {"roc_min": 0.3, "ema": 50}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ema = df["close"].ewm(span=self.params["ema"], adjust=False).mean()
        up = (df["roc"] > self.params["roc_min"]) & (df["close"] > ema)
        dn = (df["roc"] < -self.params["roc_min"]) & (df["close"] < ema)
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        return to_dir(up, dn)


class RegimeAdaptiveTrend(Strategy):
    key = "regime_adaptive_trend"
    name = "Regime Adaptive Trend"
    category = "trend"
    description = "Adapts EMA speed to volatility regime (ATR percentile)."
    default_params = {}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        atr_pct = df["atr"].rolling(100, min_periods=20).rank(pct=True)
        fast_span = 9
        slow_span = 30
        fast = df["close"].ewm(span=fast_span, adjust=False).mean()
        slow = df["close"].ewm(span=slow_span, adjust=False).mean()
        calm = atr_pct < 0.7
        up = cross_up(fast, slow) & calm & (df["adx"] > 20)
        dn = cross_down(fast, slow) & calm & (df["adx"] > 20)
        return to_dir(up, dn)
