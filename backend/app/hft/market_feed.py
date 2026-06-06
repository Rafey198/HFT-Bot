"""HFT-style market feed engine.

Streams tick events. If real tick data is available it replays it directly;
otherwise it converts OHLCV candles into a simulated intrabar tick stream
(clearly labelled as simulated).
"""
from __future__ import annotations

from typing import Dict, Iterator, List, Optional

import numpy as np
import pandas as pd

from ..core.config import symbol_spec
from ..core.utils import now_iso


class MarketFeed:
    def __init__(self, df: pd.DataFrame, symbol: str = "XAUUSD",
                 kind: str = "ohlcv", ticks_per_candle: int = 6):
        self.symbol = symbol
        self.kind = kind
        self.spec = symbol_spec(symbol)
        self.df = df.reset_index(drop=True)
        self.ticks_per_candle = ticks_per_candle
        self._events: List[Dict] = []
        self._build_events()
        self.total = len(self._events)

    def _half_spread(self, jitter: float = 1.0) -> float:
        return self.spec["point"] * self.spec["spread_points"] / 2.0 * jitter

    def _build_events(self) -> None:
        if self.kind == "tick" and {"bid", "ask"}.issubset(self.df.columns):
            for _, r in self.df.iterrows():
                bid = float(r["bid"])
                ask = float(r["ask"])
                mid = (bid + ask) / 2
                self._events.append({
                    "timestamp": str(r["timestamp"]),
                    "symbol": self.symbol, "bid": round(bid, 5), "ask": round(ask, 5),
                    "mid": round(mid, 5), "spread": round(ask - bid, 5),
                    "volume": float(r.get("volume", 1)), "source": "tick",
                })
            return

        # Simulate ticks inside each candle.
        rng = np.random.default_rng(42)
        n_sub = self.ticks_per_candle
        for _, r in self.df.iterrows():
            o, h, l, c = float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])
            vol = float(r.get("volume", 1))
            ts = pd.to_datetime(r["timestamp"], utc=True)
            # Path: bullish candle goes open->low->high->close, bearish open->high->low->close.
            if c >= o:
                path = [o, l, h, c]
            else:
                path = [o, h, l, c]
            # Interpolate sub-ticks along the path.
            seg = max(1, n_sub // (len(path) - 1))
            mids: List[float] = []
            for a, b in zip(path[:-1], path[1:]):
                mids.extend(np.linspace(a, b, seg, endpoint=False))
            mids.append(c)
            for j, mid in enumerate(mids):
                jitter = 1 + abs(rng.standard_normal()) * 0.3
                hs = self._half_spread(jitter)
                self._events.append({
                    "timestamp": str(ts + pd.Timedelta(seconds=j)),
                    "symbol": self.symbol,
                    "bid": round(mid - hs, 5), "ask": round(mid + hs, 5),
                    "mid": round(mid, 5), "spread": round(2 * hs, 5),
                    "volume": round(vol / max(1, len(mids)), 2),
                    "source": "simulated_tick" if self.kind == "ohlcv" else "candle_replay",
                })

    def __len__(self) -> int:
        return self.total

    def event_at(self, idx: int) -> Optional[Dict]:
        if 0 <= idx < self.total:
            ev = dict(self._events[idx])
            ev["timestamp"] = ev["timestamp"] or now_iso()
            return ev
        return None

    def iterate(self, start: int = 0) -> Iterator[Dict]:
        for i in range(start, self.total):
            yield self._events[i]
