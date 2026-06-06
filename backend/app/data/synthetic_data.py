"""Synthetic XAUUSD/Forex data generator (clearly labelled as simulated)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from ..core.config import TIMEFRAME_MINUTES, symbol_spec


def generate_ohlcv(symbol: str = "XAUUSD", timeframe: str = "M5",
                   years: float = 10.0, seed: int = 7) -> pd.DataFrame:
    """Generate realistic-looking synthetic OHLCV candles.

    Uses a regime-switching geometric random walk with intraday seasonality
    so the data exhibits trends, ranges, and volatility clusters. Clearly
    simulated — not real market data.
    """
    rng = np.random.default_rng(seed + hash(symbol) % 9973)
    spec = symbol_spec(symbol)
    minutes = TIMEFRAME_MINUTES.get(timeframe, 5)

    total_minutes = int(years * 365 * 24 * 60)
    n = max(500, total_minutes // minutes)
    n = min(n, 200_000)  # cap to keep things fast

    base_price = spec["price"]
    base_vol = spec["vol"] * np.sqrt(minutes)

    # Regime-switching drift / volatility multipliers.
    drift = np.zeros(n)
    vol_mult = np.ones(n)
    regime_len = max(50, n // 60)
    i = 0
    while i < n:
        seg = min(regime_len + int(rng.integers(-regime_len // 2, regime_len // 2)), n - i)
        seg = max(seg, 10)
        rkind = rng.choice(["trend_up", "trend_down", "range", "volatile"],
                           p=[0.28, 0.22, 0.35, 0.15])
        if rkind == "trend_up":
            drift[i:i + seg] = base_vol * rng.uniform(0.05, 0.18)
            vol_mult[i:i + seg] = rng.uniform(0.8, 1.2)
        elif rkind == "trend_down":
            drift[i:i + seg] = -base_vol * rng.uniform(0.05, 0.18)
            vol_mult[i:i + seg] = rng.uniform(0.8, 1.3)
        elif rkind == "range":
            drift[i:i + seg] = 0.0
            vol_mult[i:i + seg] = rng.uniform(0.5, 0.9)
        else:
            drift[i:i + seg] = base_vol * rng.uniform(-0.1, 0.1)
            vol_mult[i:i + seg] = rng.uniform(1.6, 2.6)
        i += seg

    shocks = rng.standard_normal(n) * base_vol * vol_mult + drift
    log_price = np.log(base_price) + np.cumsum(shocks)
    close = np.exp(log_price)

    # Build OHLC from close path with intrabar noise.
    open_ = np.empty(n)
    open_[0] = base_price
    open_[1:] = close[:-1]
    intrabar = np.abs(rng.standard_normal(n)) * base_vol * vol_mult * close
    high = np.maximum(open_, close) + intrabar * rng.uniform(0.2, 1.0, n)
    low = np.minimum(open_, close) - intrabar * rng.uniform(0.2, 1.0, n)
    volume = (rng.uniform(0.5, 1.5, n) * 1000 * vol_mult).round()

    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(minutes=minutes * (n - 1))
    idx = pd.date_range(start=start, periods=n, freq=f"{minutes}min", tz="UTC")

    # Intraday volume seasonality (busier London/NY).
    hours = idx.hour.to_numpy()
    season = np.where((hours >= 7) & (hours <= 16), 1.4, 0.8)
    volume = (volume * season).round()

    df = pd.DataFrame({
        "timestamp": idx,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })
    return df


def generate_ticks(symbol: str = "XAUUSD", hours: float = 6.0, seed: int = 11) -> pd.DataFrame:
    """Generate a synthetic tick stream (timestamp, bid, ask, volume)."""
    rng = np.random.default_rng(seed + hash(symbol) % 7919)
    spec = symbol_spec(symbol)
    n = min(int(hours * 3600 * 2), 120_000)  # ~2 ticks/sec
    base_vol = spec["vol"] * 0.04
    shocks = rng.standard_normal(n) * base_vol
    mid = spec["price"] * np.exp(np.cumsum(shocks))
    half_spread = spec["point"] * spec["spread_points"] / 2.0
    spread_jitter = (1 + np.abs(rng.standard_normal(n)) * 0.4)
    bid = mid - half_spread * spread_jitter
    ask = mid + half_spread * spread_jitter
    end = datetime.now(timezone.utc)
    ts = pd.date_range(end=end, periods=n, freq="500ms", tz="UTC")
    df = pd.DataFrame({
        "timestamp": ts,
        "bid": bid,
        "ask": ask,
        "volume": rng.integers(1, 8, n),
    })
    return df
