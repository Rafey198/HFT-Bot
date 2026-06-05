"""Execution agent — orchestrates the full pre-trade pipeline.

Signal -> Spread Guard -> Risk Manager -> Execution Queue -> Broker -> Journal
"""
from __future__ import annotations

from typing import Dict, Optional

from ..core.logging import get_logger

log = get_logger("execution.agent")


class ExecutionAgent:
    def __init__(self, spread_guard, risk_manager, execution_queue, broker,
                 journal=None, position_manager=None):
        self.spread_guard = spread_guard
        self.rm = risk_manager
        self.queue = execution_queue
        self.broker = broker
        self.journal = journal
        self.position_manager = position_manager

    def process_signal(self, signal: Dict, tick: Dict, recent_vol: float = 0.0,
                       atr: float = 0.0, regime: str = "") -> Dict:
        symbol = signal.get("symbol", "XAUUSD")
        side = signal.get("side")

        def blocked(reason: str, stage: str) -> Dict:
            payload = {
                "action": "blocked", "symbol": symbol, "side": side,
                "lot_size": 0, "entry": signal.get("entry", 0),
                "stop_loss": signal.get("stop_loss", 0),
                "take_profit": signal.get("take_profit", 0),
                "status": "blocked", "reason": f"{stage}:{reason}",
            }
            self.queue.reject(signal, f"{stage}:{reason}")
            if self.journal:
                self.journal.log_blocked(signal, reason, regime)
            return payload

        if side == "hold" or side not in ("buy", "sell"):
            return {"action": "hold", "symbol": symbol, "side": "hold",
                    "lot_size": 0, "entry": 0, "stop_loss": 0, "take_profit": 0,
                    "status": "simulated", "reason": "hold_signal"}

        # 1) Spread guard.
        sg = self.spread_guard.check(tick, signal, recent_vol=recent_vol, atr=atr)
        if not sg["allowed"]:
            return blocked(",".join(sg["blocked_by"]), "spread_guard")

        # 2) Risk manager (authoritative).
        rc = self.rm.check(signal, spread_points=sg["spread"])
        if not rc["trade_allowed"]:
            return blocked(",".join(rc["blocked_by"]), "risk_manager")

        # 3) Execution queue -> broker fill.
        def fill(order: Dict) -> Dict:
            pos = self.broker.place_order(order)
            self.rm.on_trade_opened()
            if self.position_manager:
                self.position_manager.on_open(pos["trade_id"])
            if self.journal:
                self.journal.log_open(pos, order, regime, rc["risk_percent"])
            return pos

        order = self.queue.submit(signal, rc["lot_size"], fill_callback=fill)
        if order["state"] != "filled":
            return blocked(order["reason"], "execution_queue")

        return {
            "action": "open", "symbol": symbol, "side": side,
            "lot_size": rc["lot_size"], "entry": order["filled_price"],
            "stop_loss": signal.get("stop_loss", 0),
            "take_profit": signal.get("take_profit", 0),
            "status": "executed" if self.broker.is_live else "simulated",
            "reason": "order_filled",
            "order_id": order["order_id"],
            "latency_ms": order["latency_ms"],
            "slippage": order["slippage"],
        }
