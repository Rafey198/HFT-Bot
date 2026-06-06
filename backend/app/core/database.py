"""SQLite storage for trades, signals, and datasets metadata."""
from __future__ import annotations

import json
import sqlite3
import threading
from typing import Any, Dict, List, Optional

from .config import DB_PATH

_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock, get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                timeframe TEXT,
                kind TEXT,
                rows INTEGER,
                start_date TEXT,
                end_date TEXT,
                path TEXT,
                quality_score REAL,
                created_at TEXT,
                report TEXT
            );

            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                symbol TEXT,
                side TEXT,
                entry_time TEXT,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                exit_time TEXT,
                exit_price REAL,
                lot_size REAL,
                pnl REAL,
                pnl_percent REAL,
                status TEXT,
                strategy TEXT,
                regime TEXT,
                risk_percent REAL,
                latency_ms REAL,
                spread REAL,
                slippage REAL,
                reason TEXT,
                mode TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                ts TEXT,
                symbol TEXT,
                side TEXT,
                strategy TEXT,
                confidence REAL,
                entry REAL,
                stop_loss REAL,
                take_profit REAL,
                status TEXT,
                blocked_reason TEXT,
                payload TEXT
            );
            """
        )
        conn.commit()


def insert_dataset(meta: Dict[str, Any]) -> None:
    with _lock, get_connection() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO datasets
            (id, symbol, timeframe, kind, rows, start_date, end_date, path, quality_score, created_at, report)
            VALUES (:id, :symbol, :timeframe, :kind, :rows, :start_date, :end_date, :path, :quality_score, :created_at, :report)""",
            {
                **meta,
                "report": json.dumps(meta.get("report", {})),
            },
        )
        conn.commit()


def list_datasets() -> List[Dict[str, Any]]:
    with _lock, get_connection() as conn:
        rows = conn.execute("SELECT * FROM datasets ORDER BY created_at DESC").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["report"] = json.loads(d.get("report") or "{}")
            except json.JSONDecodeError:
                d["report"] = {}
            out.append(d)
        return out


def get_dataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    with _lock, get_connection() as conn:
        r = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        try:
            d["report"] = json.loads(d.get("report") or "{}")
        except json.JSONDecodeError:
            d["report"] = {}
        return d


def insert_trade(trade: Dict[str, Any]) -> None:
    cols = [
        "trade_id", "symbol", "side", "entry_time", "entry_price", "stop_loss",
        "take_profit", "exit_time", "exit_price", "lot_size", "pnl", "pnl_percent",
        "status", "strategy", "regime", "risk_percent", "latency_ms", "spread",
        "slippage", "reason", "mode", "created_at",
    ]
    record = {c: trade.get(c) for c in cols}
    with _lock, get_connection() as conn:
        placeholders = ", ".join(f":{c}" for c in cols)
        conn.execute(
            f"INSERT OR REPLACE INTO trades ({', '.join(cols)}) VALUES ({placeholders})",
            record,
        )
        conn.commit()


def list_trades(mode: Optional[str] = None, status: Optional[str] = None,
                strategy: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
    query = "SELECT * FROM trades WHERE 1=1"
    params: List[Any] = []
    if mode:
        query += " AND mode = ?"
        params.append(mode)
    if status:
        query += " AND status = ?"
        params.append(status)
    if strategy:
        query += " AND strategy = ?"
        params.append(strategy)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with _lock, get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def insert_signal(signal: Dict[str, Any]) -> None:
    with _lock, get_connection() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO signals
            (signal_id, ts, symbol, side, strategy, confidence, entry, stop_loss, take_profit, status, blocked_reason, payload)
            VALUES (:signal_id, :ts, :symbol, :side, :strategy, :confidence, :entry, :stop_loss, :take_profit, :status, :blocked_reason, :payload)""",
            {
                "signal_id": signal.get("signal_id"),
                "ts": signal.get("timestamp") or signal.get("ts"),
                "symbol": signal.get("symbol"),
                "side": signal.get("side"),
                "strategy": signal.get("strategy"),
                "confidence": signal.get("confidence"),
                "entry": signal.get("entry"),
                "stop_loss": signal.get("stop_loss"),
                "take_profit": signal.get("take_profit"),
                "status": signal.get("status", "scanned"),
                "blocked_reason": signal.get("blocked_reason", ""),
                "payload": json.dumps(signal, default=str),
            },
        )
        conn.commit()
