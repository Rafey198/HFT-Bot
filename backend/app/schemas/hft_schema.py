from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TickEvent(BaseModel):
    timestamp: str = ""
    symbol: str = "XAUUSD"
    bid: float = 0
    ask: float = 0
    mid: float = 0
    spread: float = 0
    volume: float = 0
    source: str = "simulated_tick"  # tick | simulated_tick | candle_replay


class HftSignal(BaseModel):
    signal_id: str = ""
    timestamp: str = ""
    symbol: str = "XAUUSD"
    side: str = "hold"  # buy | sell | hold
    confidence: float = 0
    strategy: str = ""
    entry: float = 0
    stop_loss: float = 0
    take_profit: float = 0
    valid_for_ms: int = 500
    reason: str = ""
    blocked_reason: str = ""


class OrderState(BaseModel):
    order_id: str = ""
    signal_id: str = ""
    state: str = "queued"
    requested_price: float = 0
    filled_price: float = 0
    latency_ms: float = 0
    slippage: float = 0
    reason: str = ""


class LatencyReport(BaseModel):
    market_feed_latency_ms: float = 0
    signal_latency_ms: float = 0
    risk_latency_ms: float = 0
    execution_latency_ms: float = 0
    broker_latency_ms: float = 0
    total_latency_ms: float = 0
    status: str = "excellent"


class SpreadGuardResult(BaseModel):
    allowed: bool = True
    spread: float = 0
    max_allowed_spread: float = 0
    slippage_estimate: float = 0
    blocked_by: List[str] = Field(default_factory=list)


class ReplayStartRequest(BaseModel):
    dataset_id: Optional[str] = None
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    speed: int = 10
    enabled_scalping: List[str] = Field(default_factory=list)
    auto_execute: bool = True


class ReplayState(BaseModel):
    running: bool = False
    paused: bool = False
    speed: int = 10
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    cursor: int = 0
    total: int = 0
    clock: str = ""
    auto_execute: bool = True
    source: str = "simulated_tick"
