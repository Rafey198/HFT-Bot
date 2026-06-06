"""Session / time-based breakout strategies."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import Strategy, to_dir


def _session_range_breakout(df: pd.DataFrame, session_col: str) -> pd.Series:
    """Breakout above/below the high/low established during a session window."""
    if session_col not in df.columns:
        return pd.Series(0, index=df.index)
    in_sess = df[session_col] == 1
    # Session group id increments each time the session restarts.
    starts = in_sess & ~in_sess.shift(1).fillna(False)
    group = starts.cumsum().where(in_sess)
    sess_high = df["high"].where(in_sess).groupby(group).cummax()
    sess_low = df["low"].where(in_sess).groupby(group).cummin()
    sess_high = sess_high.ffill()
    sess_low = sess_low.ffill()
    up = (df["close"] > sess_high.shift(1)) & ~in_sess
    dn = (df["close"] < sess_low.shift(1)) & ~in_sess
    up = up & ~up.shift(1).fillna(False)
    dn = dn & ~dn.shift(1).fillna(False)
    return to_dir(up.fillna(False), dn.fillna(False))


class LondonBreakout(Strategy):
    key = "london_breakout"
    name = "London Breakout"
    category = "session"
    description = "Breakout of the range built during the London session."
    sl_atr = 1.5
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return _session_range_breakout(df, "london_session")


class NewYorkBreakout(Strategy):
    key = "new_york_breakout"
    name = "New York Breakout"
    category = "session"
    description = "Breakout of the range built during the New York session."
    sl_atr = 1.5
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return _session_range_breakout(df, "ny_session")


class AsianRangeBreakout(Strategy):
    key = "asian_range_breakout"
    name = "Asian Range Breakout"
    category = "session"
    description = "Trade the breakout of the typically tight Asian session range."
    sl_atr = 1.2
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return _session_range_breakout(df, "asian_session")


class OpeningRangeBreakout(Strategy):
    key = "opening_range_breakout"
    name = "Opening Range Breakout"
    category = "session"
    description = "Break of the first N-bar range of each trading day."
    default_params = {"or_bars": 12}
    sl_atr = 1.3
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ts = pd.to_datetime(df["timestamp"], utc=True)
        day = ts.dt.date
        bar_in_day = df.groupby(day).cumcount()
        n = self.params["or_bars"]
        opening = bar_in_day < n
        or_high = df["high"].where(opening).groupby(day).transform("max")
        or_low = df["low"].where(opening).groupby(day).transform("min")
        after = bar_in_day >= n
        up = (df["close"] > or_high) & after
        dn = (df["close"] < or_low) & after
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        return to_dir(up.fillna(False), dn.fillna(False))
