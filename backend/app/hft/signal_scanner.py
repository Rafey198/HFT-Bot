"""HFT-style signal scanner — fast lightweight strategies run on every tick.

Operates on a rolling window of recent ticks. Signals expire quickly and never
emit without a stop loss / take profit.
"""
from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Optional

import numpy as np

from ..core.utils import new_id
from ..features.sessions import current_session

SCALPING_STRATEGIES = [
    {"key": "micro_ema_cross", "name": "Micro EMA Cross"},
    {"key": "spread_safe_momentum", "name": "Spread-Safe Momentum"},
    {"key": "tick_impulse", "name": "Tick Impulse Detection"},
    {"key": "volatility_burst", "name": "Volatility Burst Detection"},
    {"key": "vwap_deviation", "name": "VWAP Deviation"},
    {"key": "micro_mean_reversion", "name": "Micro Mean Reversion"},
    {"key": "tick_breakout", "name": "Breakout of Last N Ticks"},
    {"key": "session_momentum", "name": "Session Momentum Filter"},
    {"key": "atr_micro_breakout", "name": "ATR Micro Breakout"},
    {"key": "candle_close_confirm", "name": "Candle Close Confirmation"},
]


class SignalScanner:
    def __init__(self, window: int = 60, enabled: Optional[List[str]] = None):
        self.window = window
        self.enabled = set(enabled) if enabled else {s["key"] for s in SCALPING_STRATEGIES}
        self.mids: Deque[float] = deque(maxlen=window)
        self.vols: Deque[float] = deque(maxlen=window)
        self.ema_fast: Optional[float] = None
        self.ema_slow: Optional[float] = None
        self.prev_ema_fast: Optional[float] = None
        self.prev_ema_slow: Optional[float] = None
        self.cum_pv = 0.0
        self.cum_v = 0.0
        self.stats: Dict[str, Dict] = {s["key"]: {"signals": 0} for s in SCALPING_STRATEGIES}

    def _micro_vol(self) -> float:
        if len(self.mids) < 5:
            return 0.0
        arr = np.array(self.mids)
        return float(np.std(np.diff(arr))) or float(np.std(arr)) * 0.1

    def _update_state(self, tick: Dict) -> None:
        mid = float(tick["mid"])
        vol = float(tick.get("volume", 1))
        self.mids.append(mid)
        self.vols.append(vol)
        self.prev_ema_fast, self.prev_ema_slow = self.ema_fast, self.ema_slow
        af, as_ = 2 / (8 + 1), 2 / (21 + 1)
        self.ema_fast = mid if self.ema_fast is None else self.ema_fast + af * (mid - self.ema_fast)
        self.ema_slow = mid if self.ema_slow is None else self.ema_slow + as_ * (mid - self.ema_slow)
        self.cum_pv += mid * vol
        self.cum_v += vol

    def _build(self, tick: Dict, strategy: str, name: str, side: str,
               confidence: float, reason: str, micro_vol: float) -> Dict:
        mid = float(tick["mid"])
        sl_dist = max(micro_vol * 4, mid * 5e-5)
        if side == "buy":
            entry = float(tick["ask"])
            sl = entry - sl_dist
            tp = entry + sl_dist * 1.5
        else:
            entry = float(tick["bid"])
            sl = entry + sl_dist
            tp = entry - sl_dist * 1.5
        self.stats[strategy]["signals"] += 1
        return {
            "signal_id": new_id("sig"),
            "timestamp": tick["timestamp"],
            "symbol": tick["symbol"],
            "side": side,
            "confidence": round(confidence, 1),
            "strategy": name,
            "strategy_key": strategy,
            "entry": round(entry, 5),
            "stop_loss": round(sl, 5),
            "take_profit": round(tp, 5),
            "valid_for_ms": 600,
            "reason": reason,
            "blocked_reason": "",
        }

    def scan(self, tick: Dict) -> List[Dict]:
        self._update_state(tick)
        if len(self.mids) < 12:
            return []
        mids = np.array(self.mids)
        mid = mids[-1]
        micro_vol = self._micro_vol()
        signals: List[Dict] = []
        hour = self._hour(tick["timestamp"])
        session = current_session(hour)

        # 1) Micro EMA cross
        if "micro_ema_cross" in self.enabled and None not in (
                self.ema_fast, self.ema_slow, self.prev_ema_fast, self.prev_ema_slow):
            if self.prev_ema_fast <= self.prev_ema_slow and self.ema_fast > self.ema_slow:
                signals.append(self._build(tick, "micro_ema_cross", "Micro EMA Cross",
                                           "buy", 62, "Micro EMA(8) crossed above EMA(21).", micro_vol))
            elif self.prev_ema_fast >= self.prev_ema_slow and self.ema_fast < self.ema_slow:
                signals.append(self._build(tick, "micro_ema_cross", "Micro EMA Cross",
                                           "sell", 62, "Micro EMA(8) crossed below EMA(21).", micro_vol))

        # 2) Spread-safe momentum
        if "spread_safe_momentum" in self.enabled:
            mom = mids[-1] - mids[-6]
            spread = float(tick.get("spread", 0))
            if abs(mom) > micro_vol * 3 and spread < micro_vol * 6:
                side = "buy" if mom > 0 else "sell"
                signals.append(self._build(tick, "spread_safe_momentum", "Spread-Safe Momentum",
                                           side, 60, "Short-term momentum with acceptable spread.", micro_vol))

        # 3) Tick impulse
        if "tick_impulse" in self.enabled and len(mids) >= 4:
            impulse = mids[-1] - mids[-2]
            if abs(impulse) > micro_vol * 4:
                side = "buy" if impulse > 0 else "sell"
                signals.append(self._build(tick, "tick_impulse", "Tick Impulse Detection",
                                           side, 58, "Sharp single-tick impulse detected.", micro_vol))

        # 4) Volatility burst
        if "volatility_burst" in self.enabled and len(self.mids) >= 20:
            recent = np.std(np.diff(mids[-10:]))
            base = np.std(np.diff(mids[:-10])) or 1e-9
            if recent > base * 2.2:
                side = "buy" if mids[-1] > mids[-5] else "sell"
                signals.append(self._build(tick, "volatility_burst", "Volatility Burst Detection",
                                           side, 55, "Volatility burst — momentum follow.", micro_vol))

        # 5) VWAP deviation
        if "vwap_deviation" in self.enabled and self.cum_v > 0:
            vwap = self.cum_pv / self.cum_v
            dev = mid - vwap
            if abs(dev) > micro_vol * 5:
                side = "sell" if dev > 0 else "buy"  # fade deviation
                signals.append(self._build(tick, "vwap_deviation", "VWAP Deviation",
                                           side, 57, "Price stretched from VWAP — mean reversion.", micro_vol))

        # 6) Micro mean reversion
        if "micro_mean_reversion" in self.enabled:
            mean = mids[-10:].mean()
            if mid < mean - micro_vol * 4:
                signals.append(self._build(tick, "micro_mean_reversion", "Micro Mean Reversion",
                                           "buy", 56, "Price below short mean — revert up.", micro_vol))
            elif mid > mean + micro_vol * 4:
                signals.append(self._build(tick, "micro_mean_reversion", "Micro Mean Reversion",
                                           "sell", 56, "Price above short mean — revert down.", micro_vol))

        # 7) Breakout of last N ticks
        if "tick_breakout" in self.enabled and len(mids) >= 20:
            hi = mids[-20:-1].max()
            lo = mids[-20:-1].min()
            if mid > hi:
                signals.append(self._build(tick, "tick_breakout", "Breakout of Last N Ticks",
                                           "buy", 61, "Broke 20-tick high.", micro_vol))
            elif mid < lo:
                signals.append(self._build(tick, "tick_breakout", "Breakout of Last N Ticks",
                                           "sell", 61, "Broke 20-tick low.", micro_vol))

        # 8) Session momentum filter
        if "session_momentum" in self.enabled and session in ("london", "new_york", "london_ny_overlap"):
            mom = mids[-1] - mids[-8]
            if abs(mom) > micro_vol * 3.5:
                side = "buy" if mom > 0 else "sell"
                signals.append(self._build(tick, "session_momentum", "Session Momentum Filter",
                                           side, 63, f"Momentum during active {session} session.", micro_vol))

        # 9) ATR micro breakout
        if "atr_micro_breakout" in self.enabled and len(mids) >= 15:
            rng = mids[-15:].max() - mids[-15:].min()
            if (mids[-1] - mids[-2]) > rng * 0.5 and rng > 0:
                signals.append(self._build(tick, "atr_micro_breakout", "ATR Micro Breakout",
                                           "buy", 57, "Expansion breakout vs micro range.", micro_vol))
            elif (mids[-2] - mids[-1]) > rng * 0.5 and rng > 0:
                signals.append(self._build(tick, "atr_micro_breakout", "ATR Micro Breakout",
                                           "sell", 57, "Expansion breakdown vs micro range.", micro_vol))

        # 10) Candle close confirmation
        if "candle_close_confirm" in self.enabled and len(mids) >= 6:
            up = all(mids[-i] > mids[-i - 1] for i in range(1, 4))
            dn = all(mids[-i] < mids[-i - 1] for i in range(1, 4))
            if up:
                signals.append(self._build(tick, "candle_close_confirm", "Candle Close Confirmation",
                                           "buy", 59, "Three consecutive higher ticks confirm.", micro_vol))
            elif dn:
                signals.append(self._build(tick, "candle_close_confirm", "Candle Close Confirmation",
                                           "sell", 59, "Three consecutive lower ticks confirm.", micro_vol))

        return signals

    @staticmethod
    def _hour(ts: str) -> int:
        try:
            return int(str(ts)[11:13])
        except (ValueError, IndexError):
            return 12
