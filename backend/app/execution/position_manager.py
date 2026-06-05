"""Position manager — monitors open positions across ticks and enforces exits."""
from __future__ import annotations

from typing import Dict, List, Optional

from ..core.logging import get_logger

log = get_logger("execution.position_manager")


class PositionManager:
    def __init__(self, broker, risk_manager, close_on_opposite: bool = False,
                 max_hold_ticks: int = 400):
        self.broker = broker
        self.rm = risk_manager
        self.close_on_opposite = close_on_opposite
        self.max_hold_ticks = max_hold_ticks
        self._tick_count = 0
        self._open_tick: Dict[str, int] = {}

    def on_open(self, trade_id: str) -> None:
        self._open_tick[trade_id] = self._tick_count

    def on_tick(self, tick: Dict, use_trailing: bool = False,
                current_signals: Optional[List[Dict]] = None) -> List[Dict]:
        self._tick_count += 1
        symbol = tick["symbol"]
        bid = float(tick["bid"])
        ask = float(tick["ask"])

        closed = self.broker.update_prices(symbol, bid, ask, use_trailing=use_trailing)

        # Timeout-based exits.
        mid = (bid + ask) / 2
        for pos in list(self.broker.positions.values()):
            opened = self._open_tick.get(pos["trade_id"], self._tick_count)
            if self._tick_count - opened > self.max_hold_ticks:
                c = self.broker.close_order(pos["trade_id"], mid, reason="timeout")
                if "error" not in c:
                    closed.append(c)

        # Opposite-signal exits.
        if self.close_on_opposite and current_signals:
            sides = {s["side"] for s in current_signals if s["side"] in ("buy", "sell")}
            for pos in list(self.broker.positions.values()):
                opposite = "sell" if pos["side"] == "buy" else "buy"
                if opposite in sides and pos["side"] not in sides:
                    c = self.broker.close_order(pos["trade_id"], mid, reason="opposite_signal")
                    if "error" not in c:
                        closed.append(c)

        # Kill switch — flatten everything.
        if self.rm.kill_switch_active and self.broker.positions:
            closed += self.broker.close_all(reason="kill_switch")

        for c in closed:
            self.rm.on_trade_closed(c["pnl"])
            self._open_tick.pop(c["trade_id"], None)
        self.rm.set_equity(self.broker.equity)
        return closed

    def reset(self) -> None:
        self._tick_count = 0
        self._open_tick.clear()
