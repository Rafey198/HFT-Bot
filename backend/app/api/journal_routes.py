from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from ..core.database import list_trades
from ..hft.tick_replay import engine

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.get("/trades")
def trades(mode: Optional[str] = None, status: Optional[str] = None,
           strategy: Optional[str] = None, limit: int = 500):
    db_trades = list_trades(mode=mode, status=status, strategy=strategy, limit=limit)
    return {
        "events": engine.journal.recent(limit),
        "blocked": list(engine.journal.blocked)[:200],
        "db_trades": db_trades,
    }


@router.get("/export")
def export(fmt: str = Query("csv")):
    if fmt == "json":
        return PlainTextResponse(engine.journal.export_json(), media_type="application/json")
    return PlainTextResponse(engine.journal.export_csv(), media_type="text/csv")
