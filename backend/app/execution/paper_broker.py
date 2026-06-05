"""Paper broker — simulates fills, tracks balance/equity, applies SL/TP/trailing."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from ..backtesting.engine import CONTRACT_SIZE
from ..core.config import symbol_spec
from ..core.logging import get_logger
from ..core.utils import new_id, now_iso

log = get_logger("execution.paper_broker")


class PaperBroker:
    name = "paper"
    is_live = False

    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.margin_used = 0.0
        self.positions: Dict[str, Dict] = {}
        self.closed: List[Dict] = []
        self.on_close: Optional[Callable[[Dict], None]] = None

    def connect(self) -> Dict:
        return {"connected": True, "broker": "paper", "balance": self.balance}

    def reset(self, initial_balance: Optional[float] = None) -> None:
        if initial_balance is not None:
            self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.equity = self.initial_balance
        self.margin_used = 0.0
        self.positions.clear()
        self.closed.clear()

    def get_quote(self, symbol: str) -> Dict:
        spec = symbol_spec(symbol)
        return {"symbol": symbol, "bid": spec["price"], "ask": spec["price"] + spec["point"] * spec["spread_points"]}

    def place_order(self, order: Dict) -> Dict:
        trade_id = new_id("ptr")
        symbol = order["symbol"]
        side = order["side"]
        entry = float(order["filled_price"] or order["requested_price"])
        position = {
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "entry_time": order.get("ts", now_iso()),
            "entry_price": round(entry, 5),
            "stop_loss": round(float(order.get("stop_loss") or 0), 5),
            "take_profit": round(float(order.get("take_profit") or 0), 5),
            "exit_time": "",
            "exit_price": 0.0,
            "lot_size": float(order.get("lot_size", 0)),
            "pnl": 0.0,
            "pnl_percent": 0.0,
            "status": "open",
            "strategy": order.get("strategy", ""),
            "reason": order.get("reason", ""),
            "trail": 0.0,
        }
        self.positions[trade_id] = position
        return position

    def _pnl(self, pos: Dict, price: float) -> float:
        contract = CONTRACT_SIZE.get(pos["symbol"].upper(), 100000.0)
        side = 1 if pos["side"] == "buy" else -1
        return (price - pos["entry_price"]) * side * contract * pos["lot_size"]

    def update_prices(self, symbol: str, bid: float, ask: float,
                      use_trailing: bool = False) -> List[Dict]:
        """Mark-to-market open positions; auto-close on SL/TP. Returns closed trades."""
        just_closed: List[Dict] = []
        mid = (bid + ask) / 2
        unrealized = 0.0
        for trade_id, pos in list(self.positions.items()):
            if pos["symbol"] != symbol:
                unrealized += self._pnl(pos, mid)
                continue
            price = bid if pos["side"] == "buy" else ask  # exit at the worse side
            exit_price = None
            reason = ""
            if use_trailing and pos["stop_loss"] > 0:
                spec = symbol_spec(symbol)
                trail_dist = spec["point"] * spec["spread_points"] * 3
                if pos["side"] == "buy":
                    pos["stop_loss"] = max(pos["stop_loss"], mid - trail_dist)
                else:
                    pos["stop_loss"] = min(pos["stop_loss"], mid + trail_dist)
            if pos["side"] == "buy":
                if pos["stop_loss"] > 0 and price <= pos["stop_loss"]:
                    exit_price, reason = pos["stop_loss"], "stop_loss"
                elif pos["take_profit"] > 0 and price >= pos["take_profit"]:
                    exit_price, reason = pos["take_profit"], "take_profit"
            else:
                if pos["stop_loss"] > 0 and price >= pos["stop_loss"]:
                    exit_price, reason = pos["stop_loss"], "stop_loss"
                elif pos["take_profit"] > 0 and price <= pos["take_profit"]:
                    exit_price, reason = pos["take_profit"], "take_profit"

            if exit_price is not None:
                closed = self._close(trade_id, exit_price, reason)
                just_closed.append(closed)
            else:
                unrealized += self._pnl(pos, price)

        self.equity = self.balance + unrealized
        return just_closed

    def _close(self, trade_id: str, price: float, reason: str) -> Dict:
        pos = self.positions.pop(trade_id)
        pnl = self._pnl(pos, price)
        self.balance += pnl
        pos.update({
            "exit_time": now_iso(),
            "exit_price": round(price, 5),
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl / self.initial_balance * 100, 3),
            "status": "closed",
            "reason": reason,
        })
        self.closed.append(pos)
        if self.on_close:
            self.on_close(pos)
        return pos

    def close_order(self, trade_id: str, price: float, reason: str = "manual") -> Dict:
        if trade_id not in self.positions:
            return {"error": "position_not_found", "trade_id": trade_id}
        return self._close(trade_id, price, reason)

    def close_all(self, reason: str = "kill_switch") -> List[Dict]:
        closed = []
        for trade_id, pos in list(self.positions.items()):
            price = pos["entry_price"]  # close at last known entry baseline
            closed.append(self._close(trade_id, price, reason))
        return closed

    def open_positions(self) -> List[Dict]:
        return list(self.positions.values())

    def state(self) -> Dict:
        return {
            "balance": round(self.balance, 2),
            "equity": round(self.equity, 2),
            "initial_balance": self.initial_balance,
            "margin_used": round(self.margin_used, 2),
            "open_positions": self.open_positions(),
            "closed_trades": self.closed[-100:],
            "open_count": len(self.positions),
            "closed_count": len(self.closed),
        }
