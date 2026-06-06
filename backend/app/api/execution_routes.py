from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..core.utils import now_iso
from ..hft.tick_replay import engine

router = APIRouter(prefix="/api/execution", tags=["execution"])


class ManualOrder(BaseModel):
    symbol: str = "XAUUSD"
    side: str = "buy"
    confidence: float = 75
    entry: float = 0
    stop_loss: float = 0
    take_profit: float = 0
    strategy: str = "manual"


class CloseRequest(BaseModel):
    trade_id: str
    price: Optional[float] = None


class KillSwitchRequest(BaseModel):
    activate: bool = True
    reason: str = "Manual kill switch"


@router.post("/order")
def manual_order(order: ManualOrder):
    tick = engine.last_tick or {
        "symbol": order.symbol, "bid": order.entry, "ask": order.entry,
        "mid": order.entry, "spread": 0, "volume": 1, "timestamp": now_iso(),
    }
    sig = {
        "signal_id": "manual_" + now_iso(),
        "timestamp": tick["timestamp"],
        "symbol": order.symbol, "side": order.side, "confidence": order.confidence,
        "strategy": order.strategy, "entry": order.entry or tick.get("ask"),
        "stop_loss": order.stop_loss, "take_profit": order.take_profit,
        "valid_for_ms": 5000, "reason": "Manual order", "blocked_reason": "",
    }
    result = engine.agent.process_signal(sig, tick, regime=engine.recent_regime.get("regime", ""))
    return result


@router.post("/close")
def close(req: CloseRequest):
    pos = engine.broker.positions.get(req.trade_id)
    price = req.price or (pos["entry_price"] if pos else 0)
    result = engine.broker.close_order(req.trade_id, price, reason="manual")
    if "error" not in result:
        engine.risk.on_trade_closed(result["pnl"])
    return result


@router.post("/kill-switch")
def kill_switch(req: KillSwitchRequest):
    return engine.kill_switch(req.activate, req.reason)
