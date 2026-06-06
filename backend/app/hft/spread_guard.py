"""Spread & slippage guard — blocks trades in poor execution conditions."""
from __future__ import annotations

from typing import Dict, List

from ..core.config import symbol_spec


class SpreadGuard:
    def __init__(self, max_spread_points: float = 30, max_slippage_points: float = 0):
        self.max_spread_points = max_spread_points
        # Default slippage cap scales with the spread cap when not provided.
        self.max_slippage_points = max_slippage_points or max_spread_points * 0.6

    def check(self, tick: Dict, signal: Dict | None = None,
              recent_vol: float = 0.0, atr: float = 0.0) -> Dict:
        symbol = tick.get("symbol", "XAUUSD")
        spec = symbol_spec(symbol)
        point = spec["point"]
        spread = float(tick.get("spread", 0))
        spread_points = spread / point if point else 0
        blocked: List[str] = []

        if spread_points > self.max_spread_points:
            blocked.append("spread_too_high")

        # Slippage estimate (points): a fraction of spread plus a small volatility term.
        vol_points = (recent_vol / point) if point else 0
        slip_points = max(0.5, spread_points * 0.15 + vol_points * 0.02)
        # Volatility spike: recent micro-volatility far above its own baseline (atr).
        if atr > 0 and recent_vol > atr * 2.5:
            blocked.append("volatility_spike")
        if slip_points > self.max_slippage_points:
            blocked.append("slippage_too_high")

        if tick.get("volume", 1) <= 0:
            blocked.append("low_liquidity")

        if signal is not None:
            valid_for = signal.get("valid_for_ms", 500)
            age = signal.get("age_ms", 0)
            if age > valid_for:
                blocked.append("stale_signal")
            if float(signal.get("confidence", 0)) < 50:
                blocked.append("low_confidence")

        return {
            "allowed": len(blocked) == 0,
            "spread": round(spread_points, 1),
            "max_allowed_spread": self.max_spread_points,
            "slippage_estimate": round(slip_points, 1),
            "blocked_by": blocked,
        }
