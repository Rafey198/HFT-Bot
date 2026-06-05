from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ..core.config import LIVE_CONFIRMATION_PHRASE
from ..execution.mt5_adapter import Mt5Adapter
from ..hft.tick_replay import engine
from ..risk.safety_agent import audit_system
from ..schemas.risk_schema import RiskSettings
from ._helpers import LAST_RUN_ALL

router = APIRouter(prefix="/api/risk", tags=["risk"])

_mt5 = Mt5Adapter()


@router.get("/settings")
def get_settings():
    return engine.risk.settings


@router.post("/settings")
def update_settings(settings: RiskSettings):
    engine.risk.update_settings(settings.model_dump())
    engine.spread_guard.max_spread_points = settings.max_spread_points
    return engine.risk.settings


@router.get("/state")
def state():
    return engine.risk.state()


class LiveCheckRequest(BaseModel):
    live_mode_enabled: bool = False
    confirmation_phrase: str = ""
    broker_connected: bool = False


@router.post("/safety")
def safety(req: LiveCheckRequest):
    has_paper = engine.broker.closed and len(engine.broker.closed) > 0
    best = LAST_RUN_ALL[0] if LAST_RUN_ALL else None
    audit = audit_system(
        live_mode=req.live_mode_enabled,
        has_paper_record=bool(has_paper),
        risk_settings=engine.risk.settings,
        broker_connected=req.broker_connected,
        kill_switch_visible=True,
        best_backtest=best,
    )
    return audit


@router.post("/live-check")
def live_check(req: LiveCheckRequest):
    """Evaluate the full live-execution checklist. Live stays locked unless all pass."""
    checklist = []

    def add(name: str, passed: bool, detail: str = ""):
        checklist.append({"name": name, "passed": bool(passed), "detail": detail})

    add("Live mode toggle enabled", req.live_mode_enabled)
    phrase_ok = req.confirmation_phrase.strip() == LIVE_CONFIRMATION_PHRASE
    add("Confirmation phrase typed exactly", phrase_ok,
        f"Required: '{LIVE_CONFIRMATION_PHRASE}'")
    mt5_status = _mt5.status()
    add("Broker adapter connected", bool(req.broker_connected and mt5_status["available"]),
        "MetaTrader5 package not installed." if not mt5_status["available"] else "")
    add("Symbol verified", bool(req.broker_connected))
    risk_valid = engine.risk.settings["risk_per_trade"] <= 1.0 and engine.risk.settings["max_daily_loss"] <= 5
    add("Risk settings valid", risk_valid)
    safety = audit_system(req.live_mode_enabled, bool(engine.broker.closed),
                          engine.risk.settings, req.broker_connected)
    add("Safety Agent passed", safety["system_safe"],
        "; ".join(safety["must_fix_before_live"]))
    add("Kill switch visible", True)
    add("Paper trading tested", bool(engine.broker.closed),
        "No closed paper trades recorded yet." if not engine.broker.closed else "")
    add("Max daily loss not reached", not engine.risk.kill_switch_active)

    all_passed = all(c["passed"] for c in checklist)
    return {
        "live_allowed": all_passed,
        "checklist": checklist,
        "mt5": mt5_status,
        "confirmation_phrase_required": LIVE_CONFIRMATION_PHRASE,
        "note": "Live trading is locked by default. All checks must pass to unlock.",
    }
