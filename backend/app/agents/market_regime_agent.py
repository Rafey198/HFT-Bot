"""Market regime agent."""
from __future__ import annotations

from typing import Dict

import pandas as pd

from ..regimes.regime_detector import detect_regime


def detect(df: pd.DataFrame) -> Dict:
    return detect_regime(df)
