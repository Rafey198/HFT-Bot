"""Momentum / oscillator strategies."""
from __future__ import annotations

import pandas as pd

from .base import Strategy, cross_down, cross_up, to_dir


class RsiReversal(Strategy):
    key = "rsi_reversal"
    name = "RSI Oversold/Overbought"
    category = "momentum"
    description = "Fade extremes: buy oversold, sell overbought."
    default_params = {"low": 30, "high": 70}
    sl_atr = 1.5
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        rsi = df["rsi"]
        up = cross_up(rsi, pd.Series(self.params["low"], index=df.index))
        dn = cross_down(rsi, pd.Series(self.params["high"], index=df.index))
        return to_dir(up, dn)


class RsiTrendPullback(Strategy):
    key = "rsi_trend_pullback"
    name = "RSI Trend Pullback"
    category = "momentum"
    description = "Buy pullbacks to RSI 40 in uptrend, sell rallies to 60 in downtrend."
    default_params = {"ema": 50}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ema = df["close"].ewm(span=self.params["ema"], adjust=False).mean()
        uptrend = df["close"] > ema
        downtrend = df["close"] < ema
        up = uptrend & cross_up(df["rsi"], pd.Series(40, index=df.index))
        dn = downtrend & cross_down(df["rsi"], pd.Series(60, index=df.index))
        return to_dir(up, dn)


class StochasticReversal(Strategy):
    key = "stochastic_reversal"
    name = "Stochastic Reversal"
    category = "momentum"
    description = "%K crossing %D in oversold/overbought zones."
    default_params = {"low": 20, "high": 80}
    sl_atr = 1.5
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        k, d = df["stoch_k"], df["stoch_d"]
        up = cross_up(k, d) & (k < self.params["low"])
        dn = cross_down(k, d) & (k > self.params["high"])
        return to_dir(up, dn)


class CciReversal(Strategy):
    key = "cci_reversal"
    name = "CCI Reversal"
    category = "momentum"
    description = "CCI crossing back from +/-100 extremes."
    default_params = {"level": 100}
    sl_atr = 1.5
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        cci = df["cci"]
        up = cross_up(cci, pd.Series(-self.params["level"], index=df.index))
        dn = cross_down(cci, pd.Series(self.params["level"], index=df.index))
        return to_dir(up, dn)


class MaRsiFilter(Strategy):
    key = "ma_rsi_filter"
    name = "Moving Average + RSI Filter"
    category = "momentum"
    description = "EMA trend with RSI momentum confirmation."
    default_params = {"ema": 50, "rsi_buy": 50, "rsi_sell": 50}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ema = df["close"].ewm(span=self.params["ema"], adjust=False).mean()
        up = cross_up(df["close"], ema) & (df["rsi"] > self.params["rsi_buy"])
        dn = cross_down(df["close"], ema) & (df["rsi"] < self.params["rsi_sell"])
        return to_dir(up, dn)


class MacdAdxFilter(Strategy):
    key = "macd_adx_filter"
    name = "MACD + ADX Filter"
    category = "momentum"
    description = "MACD crossovers filtered by ADX strength."
    default_params = {"adx_min": 22}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        strong = df["adx"] > self.params["adx_min"]
        up = cross_up(df["macd"], df["macd_signal"]) & strong
        dn = cross_down(df["macd"], df["macd_signal"]) & strong
        return to_dir(up, dn)
