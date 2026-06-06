"""Data ingestion agent (wrapper around data.ingestion)."""
from __future__ import annotations

from typing import Dict

from ..data import ingestion


def ingest(content: bytes, symbol: str, timeframe: str | None = None) -> Dict:
    return ingestion.ingest_csv(content, symbol, timeframe)


def generate_demo(symbol: str = "XAUUSD", timeframe: str = "M5",
                  years: float = 10.0, kind: str = "ohlcv") -> Dict:
    return ingestion.generate_demo(symbol, timeframe, years, kind)
