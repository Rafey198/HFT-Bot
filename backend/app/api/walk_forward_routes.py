from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..agents import walk_forward_agent
from ..backtesting.engine import BacktestConfig
from ..schemas.trade_schema import WalkForwardRequest
from ._helpers import load_df

router = APIRouter(prefix="/api/walk-forward", tags=["walk-forward"])


@router.post("/run")
def run(req: WalkForwardRequest):
    try:
        df, meta = load_df(req.dataset_id, req.symbol, req.timeframe)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    if meta["kind"] == "tick":
        raise HTTPException(status_code=400, detail="Walk-forward requires OHLCV data.")
    cfg = BacktestConfig(
        symbol=req.symbol, timeframe=req.timeframe,
        initial_balance=req.initial_balance, risk_per_trade=req.risk_per_trade,
        spread_points=req.spread_points, commission_per_lot=req.commission_per_lot,
        slippage_points=req.slippage_points, max_open_trades=req.max_open_trades,
    )
    return walk_forward_agent.run(df, req.strategy_key, cfg,
                                  req.train_months, req.test_months)
