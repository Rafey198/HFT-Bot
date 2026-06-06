from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..agents import market_regime_agent, strategy_selection_agent
from ._helpers import LAST_RUN_ALL, load_df

router = APIRouter(prefix="/api/regime", tags=["regime"])


class RegimeRequest(BaseModel):
    dataset_id: Optional[str] = None
    symbol: str = "XAUUSD"
    timeframe: str = "M5"


@router.post("/detect")
def detect(req: RegimeRequest):
    try:
        df, meta = load_df(req.dataset_id, req.symbol, req.timeframe)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    regime = market_regime_agent.detect(df)
    selection = None
    if LAST_RUN_ALL:
        selection = strategy_selection_agent.select(df, LAST_RUN_ALL)
    return {"regime": regime, "selection": selection}
