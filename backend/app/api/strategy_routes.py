from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..agents import strategy_library_agent
from ..features.pipeline import build_features
from ..schemas.strategy_schema import RunStrategyRequest
from ..strategies.registry import get_strategy
from ._helpers import load_df

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("/list")
def list_strategies():
    info = strategy_library_agent.list_all()
    return {"count": len(info), "strategies": info,
            "categories": strategy_library_agent.categories()}


@router.post("/run")
def run_strategy(req: RunStrategyRequest):
    try:
        df, meta = load_df(req.dataset_id, req.symbol, req.timeframe)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    df, _ = build_features(df)
    try:
        strat = get_strategy(req.strategy_key, req.parameters)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown strategy")
    dirs = strat.directions(df)
    n_buy = int((dirs > 0).sum())
    n_sell = int((dirs < 0).sum())
    last_signal = strat.signal_at(df, len(df) - 1)
    return {
        "strategy": strat.info(),
        "buy_signals": n_buy,
        "sell_signals": n_sell,
        "total_signals": n_buy + n_sell,
        "latest_signal": last_signal,
    }
