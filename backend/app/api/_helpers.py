"""Shared route helpers + tiny in-memory caches."""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import pandas as pd

from ..data import ingestion

# In-memory caches (process-local). Fine for a single-user research tool.
LAST_BACKTESTS: Dict[str, Dict] = {}
LAST_RUN_ALL: list = []


def load_df(dataset_id: Optional[str], symbol: str, timeframe: str,
            kind: str = "ohlcv") -> Tuple[pd.DataFrame, Dict]:
    if dataset_id:
        return ingestion.load_dataset(dataset_id)
    return ingestion.get_or_create_default(symbol, timeframe, kind)
