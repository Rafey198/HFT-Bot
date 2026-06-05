"""Fixed-fractional position sizing (no martingale, no averaging down)."""
from __future__ import annotations

from ..backtesting.engine import CONTRACT_SIZE


def compute_lot_size(balance: float, risk_percent: float, entry: float,
                     stop_loss: float, symbol: str = "XAUUSD") -> float:
    sl_distance = abs(entry - stop_loss)
    if sl_distance <= 0:
        return 0.0
    contract = CONTRACT_SIZE.get(symbol.upper(), 100000.0)
    risk_amount = balance * (risk_percent / 100.0)
    lot = risk_amount / (sl_distance * contract)
    return round(max(0.0, min(lot, 100.0)), 3)


def reward_risk_ratio(entry: float, stop_loss: float, take_profit: float) -> float:
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    if risk <= 0:
        return 0.0
    return round(reward / risk, 2)
