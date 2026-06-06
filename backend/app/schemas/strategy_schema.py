from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StrategyInfo(BaseModel):
    name: str
    key: str
    category: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class Signal(BaseModel):
    signal: str = "hold"  # buy | sell | hold
    entry_price: float = 0
    stop_loss: float = 0
    take_profit: float = 0
    confidence: float = 0
    reason: str = ""
    invalid_if: str = ""
    strategy_name: str = ""


class StrategyListResponse(BaseModel):
    count: int
    strategies: List[StrategyInfo]


class RunStrategyRequest(BaseModel):
    strategy_key: str
    dataset_id: Optional[str] = None
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    parameters: Dict[str, Any] = Field(default_factory=dict)
