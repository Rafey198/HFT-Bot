"""News-filter placeholder + ensemble voting strategy."""
from __future__ import annotations

import pandas as pd

from .base import Strategy, to_dir


class NewsFilterPlaceholder(Strategy):
    key = "news_filter"
    name = "News Filter Placeholder Strategy"
    category = "ensemble"
    description = (
        "Placeholder that stands down around high-volatility 'news-like' spikes. "
        "Real news feed integration is out of scope; this avoids trading during "
        "abnormal volatility windows."
    )
    sl_atr = 1.5
    tp_atr = 2.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        spike = df["atr"] > df["atr"].rolling(50, min_periods=10).mean() * 2.0
        ema = df["close"].ewm(span=21, adjust=False).mean()
        # Only trade calm continuation, explicitly skip spike bars.
        calm = ~spike
        up = (df["close"] > ema) & calm & (df["close"].shift(1) <= ema.shift(1))
        dn = (df["close"] < ema) & calm & (df["close"].shift(1) >= ema.shift(1))
        return to_dir(up.fillna(False), dn.fillna(False))

    def _reason(self, df, i, side):
        return "Trend continuation taken outside of abnormal (news-like) volatility spikes."


class EnsembleVoting(Strategy):
    key = "ensemble_voting"
    name = "Ensemble Voting Strategy"
    category = "ensemble"
    description = "Combines votes from several base strategies; trades only on consensus."
    default_params = {"min_votes": 2}
    sl_atr = 1.5
    tp_atr = 2.5

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Lazy import to avoid circular dependency with registry.
        from .momentum_strategies import MaRsiFilter, MacdAdxFilter
        from .trend_strategies import EmaCrossover, SupertrendFollowing
        from .volatility_strategies import DonchianBreakout

        members = [EmaCrossover(), SupertrendFollowing(), MacdAdxFilter(),
                   MaRsiFilter(), DonchianBreakout()]
        votes = sum(m.generate_signals(df).fillna(0) for m in members)
        min_v = self.params["min_votes"]
        up = votes >= min_v
        dn = votes <= -min_v
        # Only enter on the bar consensus first forms.
        up = up & ~up.shift(1).fillna(False)
        dn = dn & ~dn.shift(1).fillna(False)
        self._votes = votes
        return to_dir(up, dn)

    def confidence(self, df: pd.DataFrame, direction: pd.Series) -> pd.Series:
        votes = getattr(self, "_votes", None)
        if votes is None:
            return super().confidence(df, direction)
        conf = (50 + votes.abs() * 12).clip(0, 100)
        return conf.where(direction != 0, 0.0)
