"""Volatility / breakout / mean-reversion strategies."""
from __future__ import annotations

import pandas as pd

from .base import Strategy, cross_down, cross_up, to_dir


class BollingerMeanReversion(Strategy):
    key = "bb_mean_reversion"
    name = "Bollinger Band Mean Reversion"
    category = "volatility"
    description = "Fade touches of the outer Bollinger Bands back to the mean."
    sl_atr = 1.5
    tp_atr = 1.8

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        up = cross_up(df["close"], df["bb_lower"])
        dn = cross_down(df["close"], df["bb_upper"])
        return to_dir(up, dn)


class BollingerBreakout(Strategy):
    key = "bb_breakout"
    name = "Bollinger Band Breakout"
    category = "volatility"
    description = "Trade expansion breakouts beyond the bands after a squeeze."
    sl_atr = 1.5
    tp_atr = 3.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        squeeze = df["bb_bandwidth"] < df["bb_bandwidth"].rolling(50, min_periods=10).quantile(0.3)
        up = cross_up(df["close"], df["bb_upper"]) & squeeze.shift(1).fillna(False)
        dn = cross_down(df["close"], df["bb_lower"]) & squeeze.shift(1).fillna(False)
        return to_dir(up, dn)


class AtrBreakout(Strategy):
    key = "atr_breakout"
    name = "ATR Breakout"
    category = "volatility"
    description = "Breakout when price moves more than N*ATR from prior close."
    default_params = {"mult": 1.0}
    sl_atr = 1.5
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        move = df["close"] - df["close"].shift(1)
        thr = self.params["mult"] * df["atr"]
        up = move > thr
        dn = move < -thr
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        return to_dir(up, dn)


class DonchianBreakout(Strategy):
    key = "donchian_breakout"
    name = "Donchian Breakout"
    category = "volatility"
    description = "Classic turtle-style channel breakout."
    sl_atr = 1.5
    tp_atr = 3.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        up = df["close"] > df["donchian_upper"].shift(1)
        dn = df["close"] < df["donchian_lower"].shift(1)
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        return to_dir(up, dn)


class VwapMeanReversion(Strategy):
    key = "vwap_mean_reversion"
    name = "VWAP Mean Reversion"
    category = "volatility"
    description = "Fade price deviations from VWAP back to fair value."
    default_params = {"dev": 1.5}
    sl_atr = 1.5
    tp_atr = 1.8

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        if "vwap" not in df.columns:
            return pd.Series(0, index=df.index)
        dev = (df["close"] - df["vwap"])
        band = self.params["dev"] * df["atr"]
        up = cross_up(dev, -band)
        dn = cross_down(dev, band)
        return to_dir(up, dn)


class MeanReversionVolFilter(Strategy):
    key = "mean_reversion_vol_filter"
    name = "Mean Reversion w/ Volatility Filter"
    category = "volatility"
    description = "RSI mean reversion only in low-volatility (ranging) regimes."
    sl_atr = 1.2
    tp_atr = 1.6

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        low_vol = df["atr"].rolling(100, min_periods=20).rank(pct=True) < 0.5
        ranging = df["adx"] < 22
        ok = low_vol & ranging
        up = cross_up(df["rsi"], pd.Series(35, index=df.index)) & ok
        dn = cross_down(df["rsi"], pd.Series(65, index=df.index)) & ok
        return to_dir(up, dn)


class GoldVolatilitySession(Strategy):
    key = "gold_volatility_session"
    name = "Gold Volatility Session Strategy"
    category = "volatility"
    description = "XAUUSD-tuned breakout focused on the London/NY overlap volatility."
    sl_atr = 1.5
    tp_atr = 3.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        active = df.get("london_ny_overlap", pd.Series(1, index=df.index)) == 1
        vol_burst = df["atr"] > df["atr"].rolling(50, min_periods=10).mean() * 1.2
        up = (df["close"] > df["donchian_upper"].shift(1)) & active & vol_burst
        dn = (df["close"] < df["donchian_lower"].shift(1)) & active & vol_burst
        return to_dir(up, dn)
