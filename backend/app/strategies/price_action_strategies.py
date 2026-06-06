"""Price-action pattern strategies."""
from __future__ import annotations

import pandas as pd

from .base import Strategy, to_dir


class SupportResistanceBounce(Strategy):
    key = "sr_bounce"
    name = "Support/Resistance Bounce"
    category = "price_action"
    description = "Bounce off rolling support/resistance zones."
    sl_atr = 1.2
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        near_support = (df["low"] <= df["support"] * 1.001) & (df["close"] > df["support"])
        near_resist = (df["high"] >= df["resistance"] * 0.999) & (df["close"] < df["resistance"])
        up = near_support & (df["close"] > df["open"])
        dn = near_resist & (df["close"] < df["open"])
        return to_dir(up.fillna(False), dn.fillna(False))


class SwingBreakout(Strategy):
    key = "swing_breakout"
    name = "Swing High/Low Breakout"
    category = "price_action"
    description = "Break of recent confirmed swing highs / lows."
    sl_atr = 1.5
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        up = df["break_of_structure_up"] == 1
        dn = df["break_of_structure_down"] == 1
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        return to_dir(up, dn)


class PinBarReversal(Strategy):
    key = "pin_bar_reversal"
    name = "Pin Bar Reversal"
    category = "price_action"
    description = "Rejection pin bars at extremes signal reversals."
    sl_atr = 1.2
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        up = (df["pin_bar_bull"] == 1) & (df["close"] < df["ema_50"])
        dn = (df["pin_bar_bear"] == 1) & (df["close"] > df["ema_50"])
        return to_dir(up, dn)


class EngulfingStrategy(Strategy):
    key = "engulfing"
    name = "Engulfing Candle Strategy"
    category = "price_action"
    description = "Bullish/bearish engulfing patterns with trend context."
    sl_atr = 1.3
    tp_atr = 2.2

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        up = (df["bull_engulf"] == 1)
        dn = (df["bear_engulf"] == 1)
        return to_dir(up, dn)


class InsideBarBreakout(Strategy):
    key = "inside_bar_breakout"
    name = "Inside Bar Breakout"
    category = "price_action"
    description = "Break of the mother bar after an inside-bar consolidation."
    sl_atr = 1.3
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ib = df["inside_bar"].shift(1) == 1
        up = ib & (df["close"] > df["high"].shift(1))
        dn = ib & (df["close"] < df["low"].shift(1))
        return to_dir(up.fillna(False), dn.fillna(False))
