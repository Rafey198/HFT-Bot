"""Trade journal — records signals, blocked trades, opens, closes."""
from __future__ import annotations

import csv
import io
import json
from collections import deque
from typing import Deque, Dict, List, Optional

from ..core.database import insert_trade
from ..core.utils import now_iso


class TradeJournal:
    def __init__(self, mode: str = "paper", max_events: int = 2000):
        self.mode = mode
        self.events: Deque[Dict] = deque(maxlen=max_events)
        self.blocked: Deque[Dict] = deque(maxlen=500)

    def log_signal(self, signal: Dict, regime: str = "") -> None:
        self.events.appendleft({
            "type": "signal", "ts": signal.get("timestamp", now_iso()),
            "symbol": signal.get("symbol"), "side": signal.get("side"),
            "strategy": signal.get("strategy"), "confidence": signal.get("confidence"),
            "regime": regime, "reason": signal.get("reason", ""),
        })

    def log_blocked(self, signal: Dict, reason: str, regime: str = "") -> None:
        rec = {
            "type": "blocked", "ts": signal.get("timestamp", now_iso()),
            "symbol": signal.get("symbol"), "side": signal.get("side"),
            "strategy": signal.get("strategy"), "confidence": signal.get("confidence"),
            "regime": regime, "reason": reason,
        }
        self.events.appendleft(rec)
        self.blocked.appendleft(rec)

    def log_open(self, position: Dict, order: Dict, regime: str = "",
                 risk_percent: float = 0.0) -> None:
        self.events.appendleft({
            "type": "open", "ts": position.get("entry_time", now_iso()),
            "trade_id": position["trade_id"], "symbol": position["symbol"],
            "side": position["side"], "strategy": position.get("strategy"),
            "entry_price": position["entry_price"], "lot_size": position["lot_size"],
            "regime": regime, "risk_percent": risk_percent,
            "latency_ms": order.get("latency_ms", 0), "slippage": order.get("slippage", 0),
        })
        insert_trade({
            **position, "regime": regime, "risk_percent": risk_percent,
            "latency_ms": order.get("latency_ms", 0), "spread": order.get("spread", 0),
            "slippage": order.get("slippage", 0), "mode": self.mode,
            "created_at": now_iso(),
        })

    def log_close(self, position: Dict, regime: str = "") -> None:
        self.events.appendleft({
            "type": "close", "ts": position.get("exit_time", now_iso()),
            "trade_id": position["trade_id"], "symbol": position["symbol"],
            "side": position["side"], "strategy": position.get("strategy"),
            "exit_price": position["exit_price"], "pnl": position["pnl"],
            "pnl_percent": position.get("pnl_percent", 0), "reason": position.get("reason"),
            "regime": regime,
        })
        insert_trade({
            **position, "regime": regime, "mode": self.mode, "created_at": now_iso(),
        })

    def recent(self, limit: int = 200, type_filter: Optional[str] = None) -> List[Dict]:
        items = list(self.events)
        if type_filter:
            items = [e for e in items if e.get("type") == type_filter]
        return items[:limit]

    def export_json(self) -> str:
        return json.dumps(list(self.events), default=str, indent=2)

    def export_csv(self) -> str:
        items = list(self.events)
        if not items:
            return ""
        keys = sorted({k for e in items for k in e.keys()})
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=keys)
        writer.writeheader()
        for e in items:
            writer.writerow(e)
        return buf.getvalue()
