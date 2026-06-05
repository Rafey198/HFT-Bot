"""Preprocessing helpers: tick->OHLCV resample, cleaning."""
from __future__ import annotations

import pandas as pd

from ..core.config import TIMEFRAME_MINUTES


def ticks_to_ohlcv(ticks: pd.DataFrame, timeframe: str = "M1") -> pd.DataFrame:
    """Resample a tick frame (timestamp, bid, ask, volume) into OHLCV using mid price."""
    minutes = TIMEFRAME_MINUTES.get(timeframe, 1)
    df = ticks.copy()
    df["mid"] = (df["bid"] + df["ask"]) / 2.0
    df = df.set_index("timestamp")
    ohlc = df["mid"].resample(f"{minutes}min").ohlc()
    vol = df["volume"].resample(f"{minutes}min").sum()
    out = ohlc.join(vol)
    out = out.dropna().reset_index()
    out.columns = ["timestamp", "open", "high", "low", "close", "volume"]
    return out


def clip_to_recent(df: pd.DataFrame, max_rows: int = 60000) -> pd.DataFrame:
    if len(df) > max_rows:
        return df.iloc[-max_rows:].reset_index(drop=True)
    return df
