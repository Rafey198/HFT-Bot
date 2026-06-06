"""Data validation + quality scoring."""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from ..core.config import TIMEFRAME_MINUTES

OHLCV_COLS = ["timestamp", "open", "high", "low", "close", "volume"]
TICK_COLS = ["timestamp", "bid", "ask", "volume"]


def detect_kind(df: pd.DataFrame) -> str:
    cols = {c.lower() for c in df.columns}
    if {"bid", "ask"}.issubset(cols):
        return "tick"
    return "ohlcv"


def infer_timeframe(df: pd.DataFrame) -> str:
    if "timestamp" not in df.columns or len(df) < 3:
        return "M5"
    deltas = df["timestamp"].diff().dropna().dt.total_seconds() / 60.0
    if deltas.empty:
        return "M5"
    median_min = float(deltas.median())
    best = "M5"
    best_diff = 1e9
    for tf, m in TIMEFRAME_MINUTES.items():
        diff = abs(m - median_min)
        if diff < best_diff:
            best_diff = diff
            best = tf
    if median_min < 1:
        return "tick"
    return best


def validate_ohlcv(df: pd.DataFrame, timeframe: str) -> Tuple[pd.DataFrame, Dict]:
    warnings: List[str] = []
    report = {
        "missing_candles": 0,
        "duplicate_rows_removed": 0,
        "invalid_rows_removed": 0,
    }

    missing_cols = [c for c in OHLCV_COLS if c not in df.columns]
    if missing_cols:
        warnings.append(f"Missing columns auto-handled: {missing_cols}")
        for c in missing_cols:
            if c == "volume":
                df["volume"] = 0
            elif c == "timestamp":
                raise ValueError("OHLCV data must include a timestamp column")
            else:
                df[c] = df.get("close", np.nan)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    before = len(df)
    df = df.dropna(subset=["timestamp"]).copy()
    report["invalid_rows_removed"] += before - len(df)

    df = df.sort_values("timestamp")
    before = len(df)
    df = df.drop_duplicates(subset=["timestamp"], keep="last")
    report["duplicate_rows_removed"] += before - len(df)

    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    before = len(df)
    bad = (
        df[["open", "high", "low", "close"]].isna().any(axis=1)
        | (df[["open", "high", "low", "close"]] <= 0).any(axis=1)
        | (df["high"] < df["low"])
    )
    if bad.any():
        df = df[~bad].copy()
        report["invalid_rows_removed"] += before - len(df)
        warnings.append(f"Removed {before - len(df)} invalid OHLC rows (zero/negative/inverted).")

    # Detect missing candles.
    if timeframe in TIMEFRAME_MINUTES and len(df) > 2:
        step = pd.Timedelta(minutes=TIMEFRAME_MINUTES[timeframe])
        full = pd.date_range(df["timestamp"].iloc[0], df["timestamp"].iloc[-1], freq=step)
        # Only count weekday gaps to avoid weekend false positives.
        present = set(df["timestamp"])
        gaps = [t for t in full if t not in present and t.weekday() < 5]
        report["missing_candles"] = len(gaps)
        if len(gaps) > len(df) * 0.05:
            warnings.append(f"Detected {len(gaps)} missing candles (>5%). Consider re-exporting data.")

    df = df.reset_index(drop=True)
    report["warnings"] = warnings
    return df, report


def validate_tick(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    warnings: List[str] = []
    report = {"missing_candles": 0, "duplicate_rows_removed": 0, "invalid_rows_removed": 0}

    if "volume" not in df.columns:
        df["volume"] = 1
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    before = len(df)
    df = df.dropna(subset=["timestamp", "bid", "ask"]).copy()
    report["invalid_rows_removed"] += before - len(df)

    df["bid"] = pd.to_numeric(df["bid"], errors="coerce")
    df["ask"] = pd.to_numeric(df["ask"], errors="coerce")
    df = df.sort_values("timestamp")
    before = len(df)
    df = df.drop_duplicates(subset=["timestamp"], keep="last")
    report["duplicate_rows_removed"] += before - len(df)

    before = len(df)
    bad = (df["bid"] <= 0) | (df["ask"] <= 0) | (df["ask"] < df["bid"])
    if bad.any():
        df = df[~bad].copy()
        report["invalid_rows_removed"] += before - len(df)
        warnings.append("Removed invalid ticks (non-positive or crossed bid/ask).")

    df = df.reset_index(drop=True)
    report["warnings"] = warnings
    return df, report


def quality_score(report: Dict, rows: int) -> float:
    if rows == 0:
        return 0.0
    penalty = 0.0
    penalty += min(40.0, report.get("missing_candles", 0) / max(rows, 1) * 100)
    penalty += min(20.0, report.get("invalid_rows_removed", 0) / max(rows, 1) * 100)
    penalty += min(10.0, report.get("duplicate_rows_removed", 0) / max(rows, 1) * 100)
    return round(max(0.0, 100.0 - penalty), 1)
