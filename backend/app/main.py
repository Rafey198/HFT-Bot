"""AurumFX HFT-Style Quant Execution Agent — FastAPI entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (backtest_routes, data_routes, execution_routes, hft_routes,
                  journal_routes, paper_routes, regime_routes, report_routes,
                  risk_routes, strategy_routes, walk_forward_routes)
from .core.config import (CORS_ORIGINS, DISCLAIMER, LIVE_CONFIRMATION_PHRASE,
                         PRIMARY_SYMBOL, SUPPORTED_SYMBOLS, SUPPORTED_TIMEFRAMES)
from .core.database import init_db
from .core.logging import get_logger

log = get_logger("main")

app = FastAPI(
    title="AurumFX HFT-Style Quant Execution Agent",
    description=(
        "HFT-style retail quant execution, backtesting, tick replay, paper "
        "trading, and risk-control terminal for XAUUSD/Forex. "
        "Research/education only — not institutional HFT, no guaranteed profit."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()
    log.info("AurumFX backend ready. Live trading is DISABLED by default.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "aurumfx", "version": "1.0.0",
            "live_trading": "disabled_by_default"}


@app.get("/")
def root():
    return {
        "name": "AurumFX HFT-Style Quant Execution Agent",
        "disclaimer": DISCLAIMER,
        "live_confirmation_phrase": LIVE_CONFIRMATION_PHRASE,
        "symbols": SUPPORTED_SYMBOLS,
        "primary_symbol": PRIMARY_SYMBOL,
        "timeframes": SUPPORTED_TIMEFRAMES,
        "docs": "/docs",
    }


for r in (data_routes, strategy_routes, backtest_routes, walk_forward_routes,
          regime_routes, hft_routes, paper_routes, execution_routes,
          risk_routes, journal_routes, report_routes):
    app.include_router(r.router)
