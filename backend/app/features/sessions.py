"""Session features (UTC-based approximations)."""
from __future__ import annotations

import pandas as pd


def add_sessions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ts = pd.to_datetime(out["timestamp"], utc=True)
    hour = ts.dt.hour
    out["hour"] = hour
    out["day_of_week"] = ts.dt.dayofweek

    # Approx session windows in UTC.
    out["asian_session"] = ((hour >= 0) & (hour < 8)).astype(int)
    out["london_session"] = ((hour >= 7) & (hour < 16)).astype(int)
    out["ny_session"] = ((hour >= 12) & (hour < 21)).astype(int)
    out["london_ny_overlap"] = ((hour >= 12) & (hour < 16)).astype(int)
    return out


def current_session(hour: int) -> str:
    if 12 <= hour < 16:
        return "london_ny_overlap"
    if 7 <= hour < 16:
        return "london"
    if 12 <= hour < 21:
        return "new_york"
    if 0 <= hour < 8:
        return "asian"
    return "off_session"
