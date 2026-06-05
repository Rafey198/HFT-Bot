from __future__ import annotations

from fastapi import APIRouter

from ..hft.signal_scanner import SCALPING_STRATEGIES
from ..hft.tick_replay import engine
from ..schemas.hft_schema import ReplayStartRequest

router = APIRouter(prefix="/api/hft", tags=["hft"])


@router.post("/replay/start")
def replay_start(req: ReplayStartRequest):
    return engine.start(req.dataset_id, req.symbol, req.timeframe, req.speed,
                        req.enabled_scalping or None, req.auto_execute)


@router.post("/replay/pause")
def replay_pause():
    return engine.pause()


@router.post("/replay/resume")
def replay_resume():
    return engine.resume()


@router.post("/replay/reset")
def replay_reset():
    return engine.reset()


@router.post("/replay/speed")
def replay_speed(speed: int):
    return engine.set_speed(speed)


@router.get("/replay/state")
def replay_state():
    return engine.state()


@router.get("/market-event")
def market_event():
    return engine.market_event()


@router.get("/signals")
def signals():
    return {"signals": engine.signals()}


@router.get("/execution-queue")
def execution_queue():
    return {"orders": engine.execution_queue()}


@router.get("/latency")
def latency():
    return engine.latency.current()


@router.get("/risk-state")
def risk_state():
    return engine.risk.state()


@router.get("/logs")
def logs():
    return {"logs": engine.logs()}


@router.get("/scalping-stats")
def scalping_stats():
    return {"strategies": engine.scalping_stats(), "catalog": SCALPING_STRATEGIES}
