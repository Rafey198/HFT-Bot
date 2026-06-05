"""Strategy selection agent."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from ..selection.strategy_selector import select_strategy


def select(df: pd.DataFrame, results: List[Dict],
           stability_by_key: Optional[Dict[str, float]] = None) -> Dict:
    return select_strategy(df, results, stability_by_key)
