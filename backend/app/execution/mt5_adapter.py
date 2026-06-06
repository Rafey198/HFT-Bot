"""Optional MetaTrader 5 adapter. Safe placeholder when MT5 is unavailable.

Live trading is DISABLED by default and requires explicit risk-manager approval.
"""
from __future__ import annotations

from typing import Dict, List

from ..core.logging import get_logger
from .broker_base import BrokerBase

log = get_logger("execution.mt5")

try:  # pragma: no cover - environment dependent
    import MetaTrader5 as mt5  # type: ignore
    MT5_AVAILABLE = True
except Exception:  # noqa: BLE001
    mt5 = None
    MT5_AVAILABLE = False


class Mt5Adapter(BrokerBase):
    name = "mt5"
    is_live = True

    def __init__(self):
        self.connected = False
        self.account = None

    def _unavailable(self) -> Dict:
        return {
            "ok": False,
            "available": False,
            "error": "MetaTrader5 package not installed in this environment.",
            "hint": "pip install MetaTrader5 (Windows only) and configure a broker terminal.",
        }

    def connect(self, login: int | None = None, password: str | None = None,
                server: str | None = None) -> Dict:
        if not MT5_AVAILABLE:
            return self._unavailable()
        try:
            ok = mt5.initialize(login=login, password=password, server=server) if login else mt5.initialize()
            if not ok:
                return {"ok": False, "available": True, "error": str(mt5.last_error())}
            self.connected = True
            self.account = mt5.account_info()._asdict() if mt5.account_info() else None
            return {"ok": True, "available": True, "account": self.account}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "available": True, "error": str(exc)}

    def verify_symbol(self, symbol: str) -> Dict:
        if not MT5_AVAILABLE:
            return self._unavailable()
        info = mt5.symbol_info(symbol)
        if info is None:
            return {"ok": False, "error": f"symbol {symbol} not found"}
        return {"ok": True, "symbol": symbol, "spread": info.spread}

    def get_quote(self, symbol: str) -> Dict:
        if not MT5_AVAILABLE:
            return self._unavailable()
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return {"ok": False, "error": "no tick"}
        return {"ok": True, "symbol": symbol, "bid": tick.bid, "ask": tick.ask,
                "spread": tick.ask - tick.bid}

    def place_order(self, order: Dict) -> Dict:
        if not MT5_AVAILABLE:
            return self._unavailable()
        # Live placement intentionally guarded; requires explicit approval upstream.
        if not order.get("risk_approved"):
            return {"ok": False, "error": "risk_manager_approval_required"}
        try:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": order["symbol"],
                "volume": float(order["lot_size"]),
                "type": mt5.ORDER_TYPE_BUY if order["side"] == "buy" else mt5.ORDER_TYPE_SELL,
                "sl": float(order.get("stop_loss", 0)),
                "tp": float(order.get("take_profit", 0)),
                "deviation": 20,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            return {"ok": result.retcode == mt5.TRADE_RETCODE_DONE,
                    "retcode": result.retcode, "order": result.order}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    def close_order(self, trade_id: str, price: float, reason: str = "manual") -> Dict:
        if not MT5_AVAILABLE:
            return self._unavailable()
        return {"ok": False, "error": "close_order not implemented in demo adapter"}

    def open_positions(self) -> List[Dict]:
        if not MT5_AVAILABLE:
            return []
        positions = mt5.positions_get() or []
        return [p._asdict() for p in positions]

    def status(self) -> Dict:
        return {
            "available": MT5_AVAILABLE,
            "connected": self.connected,
            "is_live": self.is_live,
            "note": "Live MT5 trading is locked by default and requires full safety checklist.",
        }
