"""Feature engineering agent."""
from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd

from ..features.pipeline import build_features


def engineer(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    return build_features(df)
