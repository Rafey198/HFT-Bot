from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..agents import backtest_agent
from ..backtesting.engine import BacktestConfig
from ..risk.safety_agent import audit_backtest
from ..schemas.trade_schema import BacktestRequest, RunAllRequest
from ._helpers import LAST_BACKTESTS, LAST_RUN_ALL, load_df

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


def _cfg(req: BacktestRequest) -> BacktestConfig:
    return BacktestConfig(
        symbol=req.symbol, timeframe=req.timeframe,
        initial_balance=req.initial_balance, risk_per_trade=req.risk_per_trade,
        spread_points=req.spread_points, commission_per_lot=req.commission_per_lot,
        slippage_points=req.slippage_points, max_open_trades=req.max_open_trades,
        use_trailing_stop=req.use_trailing_stop,
    )


@router.post("/run")
def run(req: BacktestRequest):
    try:
        df, meta = load_df(req.dataset_id, req.symbol, req.timeframe)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    if meta["kind"] == "tick":
        raise HTTPException(status_code=400, detail="Backtests require OHLCV data.")
    result = backtest_agent.run_one(df, req.strategy_key, _cfg(req), req.parameters)
    result["safety"] = audit_backtest(result)
    LAST_BACKTESTS[req.strategy_key] = result
    return result


@router.post("/run-all")
def run_all(req: RunAllRequest):
    try:
        df, meta = load_df(req.dataset_id, req.symbol, req.timeframe)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    if meta["kind"] == "tick":
        raise HTTPException(status_code=400, detail="Backtests require OHLCV data.")
    results = backtest_agent.run_all(df, _cfg(req))
    LAST_RUN_ALL.clear()
    LAST_RUN_ALL.extend(results)
    return {"count": len(results), "results": results[: req.top_n or 35]}


@router.get("/results")
def results():
    return {"single": list(LAST_BACKTESTS.values()), "leaderboard": LAST_RUN_ALL}
