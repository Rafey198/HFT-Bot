"""Execution queue — order lifecycle with latency/spread/slippage simulation."""
from __future__ import annotations

import random
from collections import deque
from typing import Callable, Deque, Dict, List, Optional

from ..core.config import symbol_spec
from ..core.utils import new_id, now_iso

ORDER_STATES = ["received", "risk_checking", "approved", "queued",
                "executing", "filled", "rejected", "expired", "cancelled"]


class ExecutionQueue:
    def __init__(self, latency_monitor=None, max_log: int = 200):
        self.latency_monitor = latency_monitor
        self.log: Deque[Dict] = deque(maxlen=max_log)
        self._recent_signature: Deque[str] = deque(maxlen=20)

    def _record(self, order: Dict) -> None:
        self.log.appendleft(order)

    def _duplicate(self, signal: Dict) -> bool:
        sig = f"{signal.get('symbol')}|{signal.get('side')}|{signal.get('strategy_key', signal.get('strategy'))}"
        if sig in self._recent_signature:
            return True
        self._recent_signature.append(sig)
        return False

    def submit(self, signal: Dict, lot_size: float,
               fill_callback: Optional[Callable[[Dict], Dict]] = None) -> Dict:
        order_id = new_id("ord")
        symbol = signal.get("symbol", "XAUUSD")
        spec = symbol_spec(symbol)
        point = spec["point"]
        requested = float(signal.get("entry", 0))
        side = signal.get("side")

        base = {
            "order_id": order_id,
            "signal_id": signal.get("signal_id", ""),
            "strategy": signal.get("strategy", ""),
            "symbol": symbol,
            "side": side,
            "lot_size": round(lot_size, 3),
            "requested_price": round(requested, 5),
            "filled_price": 0.0,
            "latency_ms": 0.0,
            "slippage": 0.0,
            "state": "received",
            "reason": "",
            "ts": now_iso(),
        }

        # Duplicate guard.
        if self._duplicate(signal):
            base.update(state="rejected", reason="duplicate_order")
            self._record(base)
            return base

        # Stale guard.
        if signal.get("age_ms", 0) > signal.get("valid_for_ms", 600):
            base.update(state="expired", reason="stale_signal")
            self._record(base)
            return base

        latency = self.latency_monitor.total_for_order() if self.latency_monitor else random.uniform(15, 60)
        base["latency_ms"] = round(latency, 2)

        # Slippage proportional to latency + randomness.
        slip_points = max(0.0, random.gauss(latency / 20.0, 1.5))
        slippage = slip_points * point
        if side == "buy":
            filled = requested + slippage
        else:
            filled = requested - slippage
        base["slippage"] = round(slippage, 5)
        base["filled_price"] = round(filled, 5)

        # Walk through visible states for the UI.
        base["state"] = "filled"
        base["reason"] = "ok"

        order_for_broker = dict(base)
        order_for_broker["stop_loss"] = signal.get("stop_loss")
        order_for_broker["take_profit"] = signal.get("take_profit")
        order_for_broker["strategy"] = signal.get("strategy", "")

        if fill_callback is not None:
            try:
                fill_callback(order_for_broker)
            except Exception as exc:  # pragma: no cover
                base.update(state="rejected", reason=f"broker_error:{exc}")
        self._record(base)
        return base

    def reject(self, signal: Dict, reason: str) -> Dict:
        order = {
            "order_id": new_id("ord"),
            "signal_id": signal.get("signal_id", ""),
            "strategy": signal.get("strategy", ""),
            "symbol": signal.get("symbol", "XAUUSD"),
            "side": signal.get("side"),
            "lot_size": 0.0,
            "requested_price": round(float(signal.get("entry", 0)), 5),
            "filled_price": 0.0,
            "latency_ms": 0.0,
            "slippage": 0.0,
            "state": "rejected",
            "reason": reason,
            "ts": now_iso(),
        }
        self._record(order)
        return order

    def recent(self, limit: int = 50) -> List[Dict]:
        return list(self.log)[:limit]
