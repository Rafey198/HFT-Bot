"""Strategy registry — single source of truth for all 35 strategies."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from .base import Strategy
from .ensemble_strategies import EnsembleVoting, NewsFilterPlaceholder
from .ml_strategy import MlClassifierStrategy
from .momentum_strategies import (CciReversal, MacdAdxFilter, MaRsiFilter,
                                  RsiReversal, RsiTrendPullback,
                                  StochasticReversal)
from .price_action_strategies import (EngulfingStrategy, InsideBarBreakout,
                                      PinBarReversal, SupportResistanceBounce,
                                      SwingBreakout)
from .session_strategies import (AsianRangeBreakout, LondonBreakout,
                                 NewYorkBreakout, OpeningRangeBreakout)
from .trend_strategies import (AdxTrendStrength, AtrTrailingTrend, EmaCrossover,
                               IchimokuCloudTrend, MacdCrossover,
                               MomentumContinuation, RegimeAdaptiveTrend,
                               SmaCrossover, SupertrendFollowing,
                               TripleEmaTrend)
from .volatility_strategies import (AtrBreakout, BollingerBreakout,
                                    BollingerMeanReversion, DonchianBreakout,
                                    GoldVolatilitySession,
                                    MeanReversionVolFilter, VwapMeanReversion)

_ALL: List[Type[Strategy]] = [
    SmaCrossover, EmaCrossover, TripleEmaTrend, MacdCrossover,
    RsiReversal, RsiTrendPullback,
    BollingerMeanReversion, BollingerBreakout,
    AtrBreakout, DonchianBreakout,
    SupertrendFollowing, AdxTrendStrength, IchimokuCloudTrend,
    StochasticReversal, CciReversal, VwapMeanReversion,
    LondonBreakout, NewYorkBreakout, AsianRangeBreakout, OpeningRangeBreakout,
    SupportResistanceBounce, SwingBreakout, PinBarReversal, EngulfingStrategy,
    InsideBarBreakout, MaRsiFilter, MacdAdxFilter, AtrTrailingTrend,
    MeanReversionVolFilter, MomentumContinuation, GoldVolatilitySession,
    NewsFilterPlaceholder, RegimeAdaptiveTrend, EnsembleVoting,
    MlClassifierStrategy,
]

REGISTRY: Dict[str, Type[Strategy]] = {cls.key: cls for cls in _ALL}


def all_keys() -> List[str]:
    return list(REGISTRY.keys())


def get_strategy(key: str, params: Optional[Dict[str, Any]] = None) -> Strategy:
    cls = REGISTRY.get(key)
    if cls is None:
        raise KeyError(f"Unknown strategy '{key}'")
    return cls(params)


def list_strategy_info() -> List[Dict[str, Any]]:
    return [cls().info() for cls in _ALL]


def category_map() -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for cls in _ALL:
        out.setdefault(cls.category, []).append(cls.key)
    return out


assert len(REGISTRY) >= 35, f"Expected >=35 strategies, got {len(REGISTRY)}"
