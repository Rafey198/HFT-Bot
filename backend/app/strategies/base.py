"""Base strategy abstraction.

Every strategy produces a vectorized direction series (-1 sell / 0 hold / 1 buy)
plus a per-bar confidence (0-100). SL/TP are derived from ATR multiples so that
*no signal is ever emitted without a stop loss*.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


class Strategy:
    key: str = "base"
    name: str = "Base Strategy"
    category: str = "generic"
    description: str = ""
    default_params: Dict[str, Any] = {}
    sl_atr: float = 1.5
    tp_atr: float = 2.5

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = {**self.default_params, **(params or {})}
        self._cache_dir: Optional[pd.Series] = None

    # --- to be overridden -------------------------------------------------
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Return a series of -1 / 0 / 1 for each bar."""
        return pd.Series(0, index=df.index)

    def confidence(self, df: pd.DataFrame, direction: pd.Series) -> pd.Series:
        """Confidence 0-100. Default: scaled by ADX trend strength."""
        adx = df.get("adx")
        if adx is None:
            base = pd.Series(60.0, index=df.index)
        else:
            base = (50 + (adx.clip(0, 50))).clip(0, 100)
        return base.where(direction != 0, 0.0)

    # --- shared -----------------------------------------------------------
    def directions(self, df: pd.DataFrame) -> pd.Series:
        if self._cache_dir is None or len(self._cache_dir) != len(df):
            self._cache_dir = self.generate_signals(df).fillna(0).astype(int)
        return self._cache_dir

    def sl_tp(self, df: pd.DataFrame, i: int, side: int) -> tuple[float, float]:
        price = float(df["close"].iloc[i])
        atr = float(df["atr"].iloc[i]) if "atr" in df.columns else price * 0.001
        atr = max(atr, price * 1e-5)
        if side > 0:
            return price - self.sl_atr * atr, price + self.tp_atr * atr
        return price + self.sl_atr * atr, price - self.tp_atr * atr

    def signal_at(self, df: pd.DataFrame, i: int) -> Dict[str, Any]:
        dirs = self.directions(df)
        side = int(dirs.iloc[i])
        price = float(df["close"].iloc[i])
        if side == 0:
            return {
                "signal": "hold", "entry_price": price, "stop_loss": 0,
                "take_profit": 0, "confidence": 0, "reason": "Conditions not met",
                "invalid_if": "", "strategy_name": self.name,
            }
        sl, tp = self.sl_tp(df, i, side)
        conf = float(self.confidence(df, dirs).iloc[i])
        return {
            "signal": "buy" if side > 0 else "sell",
            "entry_price": round(price, 5),
            "stop_loss": round(sl, 5),
            "take_profit": round(tp, 5),
            "confidence": round(conf, 1),
            "reason": self._reason(df, i, side),
            "invalid_if": "Price closes beyond stop loss before target.",
            "strategy_name": self.name,
        }

    def _reason(self, df: pd.DataFrame, i: int, side: int) -> str:
        return f"{self.name} triggered a {'long' if side > 0 else 'short'} setup."

    def info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "key": self.key,
            "category": self.category,
            "description": self.description,
            "parameters": self.params,
            "enabled": True,
        }


def cross_up(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a > b) & (a.shift(1) <= b.shift(1))


def cross_down(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a < b) & (a.shift(1) >= b.shift(1))


def to_dir(buy: pd.Series, sell: pd.Series) -> pd.Series:
    d = pd.Series(0, index=buy.index)
    d[buy.fillna(False)] = 1
    d[sell.fillna(False)] = -1
    return d
