"""Data ingestion agent: load CSV / synthetic, validate, persist."""
from __future__ import annotations

import io
from typing import Dict, Optional, Tuple

import pandas as pd

from ..core.config import CLEAN_DIR, PRIMARY_SYMBOL
from ..core.database import get_dataset, insert_dataset, list_datasets
from ..core.logging import get_logger
from ..core.utils import new_id, now_iso
from . import synthetic_data, validation

log = get_logger("data.ingestion")


def _persist(df: pd.DataFrame, symbol: str, timeframe: str, kind: str,
             report: Dict) -> Dict:
    dataset_id = new_id("ds")
    path = CLEAN_DIR / f"{dataset_id}.parquet"
    try:
        df.to_parquet(path)
    except Exception:  # pragma: no cover - fallback when pyarrow missing
        path = CLEAN_DIR / f"{dataset_id}.csv"
        df.to_csv(path, index=False)
    start = str(df["timestamp"].iloc[0]) if len(df) else ""
    end = str(df["timestamp"].iloc[-1]) if len(df) else ""
    score = validation.quality_score(report, len(df))
    meta = {
        "id": dataset_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "kind": kind,
        "rows": len(df),
        "start_date": start,
        "end_date": end,
        "path": str(path),
        "quality_score": score,
        "created_at": now_iso(),
        "report": {
            "symbol": symbol,
            "timeframe": timeframe,
            "rows": len(df),
            "start_date": start,
            "end_date": end,
            "missing_candles": report.get("missing_candles", 0),
            "duplicate_rows_removed": report.get("duplicate_rows_removed", 0),
            "invalid_rows_removed": report.get("invalid_rows_removed", 0),
            "data_quality_score": score,
            "warnings": report.get("warnings", []),
            "kind": kind,
            "dataset_id": dataset_id,
        },
    }
    insert_dataset(meta)
    return meta


def ingest_csv(content: bytes, symbol: str, timeframe: Optional[str] = None) -> Dict:
    df = pd.read_csv(io.BytesIO(content))
    df.columns = [c.strip().lower() for c in df.columns]
    kind = validation.detect_kind(df)

    if kind == "tick":
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df, report = validation.validate_tick(df)
        tf = "tick"
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        tf = timeframe or validation.infer_timeframe(df)
        df, report = validation.validate_ohlcv(df, tf)

    meta = _persist(df, symbol or PRIMARY_SYMBOL, tf, kind, report)
    log.info("Ingested %s rows for %s/%s (%s)", len(df), symbol, tf, kind)
    return meta["report"] | {"dataset_id": meta["id"]}


def generate_demo(symbol: str = "XAUUSD", timeframe: str = "M5",
                  years: float = 10.0, kind: str = "ohlcv") -> Dict:
    if kind == "tick":
        df = synthetic_data.generate_ticks(symbol, hours=max(1.0, years))
        df, report = validation.validate_tick(df)
        report["warnings"] = (report.get("warnings", []) +
                              ["SIMULATED tick data — not real market data."])
        meta = _persist(df, symbol, "tick", "tick", report)
    else:
        df = synthetic_data.generate_ohlcv(symbol, timeframe, years)
        df, report = validation.validate_ohlcv(df, timeframe)
        report["warnings"] = (report.get("warnings", []) +
                              ["SIMULATED OHLCV data — not real market data."])
        meta = _persist(df, symbol, timeframe, "ohlcv", report)
    log.info("Generated demo %s %s %s rows", symbol, timeframe, meta["rows"])
    return meta["report"] | {"dataset_id": meta["id"]}


def load_dataset(dataset_id: str) -> Tuple[pd.DataFrame, Dict]:
    meta = get_dataset(dataset_id)
    if not meta:
        raise FileNotFoundError(f"Dataset {dataset_id} not found")
    path = meta["path"]
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    return df, meta


def get_or_create_default(symbol: str = "XAUUSD", timeframe: str = "M5",
                          kind: str = "ohlcv") -> Tuple[pd.DataFrame, Dict]:
    """Return a usable dataset, generating demo data if none exists."""
    for ds in list_datasets():
        if ds["symbol"] == symbol and ds["timeframe"] == timeframe and ds["kind"] == kind:
            return load_dataset(ds["id"])
    report = generate_demo(symbol, timeframe, years=10.0 if kind == "ohlcv" else 6.0, kind=kind)
    return load_dataset(report["dataset_id"])
