from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..core.database import list_trades
from ..hft.tick_replay import engine
from ..reports.report_generator import backtest_report, paper_report
from ._helpers import LAST_BACKTESTS, LAST_RUN_ALL

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/backtest")
def backtest(strategy_key: str = ""):
    if strategy_key and strategy_key in LAST_BACKTESTS:
        result = LAST_BACKTESTS[strategy_key]
    elif LAST_BACKTESTS:
        result = list(LAST_BACKTESTS.values())[-1]
    elif LAST_RUN_ALL:
        result = LAST_RUN_ALL[0]
    else:
        raise HTTPException(status_code=404, detail="No backtest results yet. Run a backtest first.")
    return backtest_report(result)


@router.get("/paper")
def paper():
    trades = list_trades(mode="paper", limit=1000)
    return paper_report(engine.broker.state(), engine.risk.state(), trades)
