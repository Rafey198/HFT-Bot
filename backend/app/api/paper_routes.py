from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..hft.tick_replay import engine

router = APIRouter(prefix="/api/paper", tags=["paper"])


class PaperStartRequest(BaseModel):
    dataset_id: Optional[str] = None
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    speed: int = 10
    enabled_scalping: List[str] = []


@router.post("/start")
def start(req: PaperStartRequest):
    return engine.start(req.dataset_id, req.symbol, req.timeframe, req.speed,
                        req.enabled_scalping or None, auto_execute=True)


@router.post("/stop")
def stop():
    engine.pause()
    return engine.state()


@router.get("/state")
def state():
    broker = engine.broker.state()
    risk = engine.risk.state()
    return {
        "broker": broker,
        "risk": risk,
        "replay": engine.state(),
        "recent_signals": engine.signals(20),
        "logs": engine.logs(40),
    }
