"""Latency monitor — measures (and for replay, simulates) pipeline latencies."""
from __future__ import annotations

import random
from collections import deque
from typing import Deque, Dict


class LatencyMonitor:
    def __init__(self):
        self.history: Deque[Dict] = deque(maxlen=120)
        self._last = self._simulate()

    def _simulate(self) -> Dict:
        feed = round(random.uniform(2, 14), 2)
        signal = round(random.uniform(1, 8), 2)
        risk = round(random.uniform(0.5, 4), 2)
        execq = round(random.uniform(1, 9), 2)
        broker = round(random.uniform(8, 45), 2)  # simulated broker round-trip
        total = round(feed + signal + risk + execq + broker, 2)
        return {
            "market_feed_latency_ms": feed,
            "signal_latency_ms": signal,
            "risk_latency_ms": risk,
            "execution_latency_ms": execq,
            "broker_latency_ms": broker,
            "total_latency_ms": total,
            "status": self._status(total),
        }

    @staticmethod
    def _status(total: float) -> str:
        if total < 40:
            return "excellent"
        if total < 80:
            return "acceptable"
        if total < 150:
            return "slow"
        return "dangerous"

    def sample(self) -> Dict:
        self._last = self._simulate()
        self.history.append(self._last)
        return self._last

    def current(self) -> Dict:
        return self._last

    def total_for_order(self) -> float:
        return self._last["total_latency_ms"]
