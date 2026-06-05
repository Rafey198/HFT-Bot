"""Walk-forward agent."""
from __future__ import annotations

from typing import Dict

import pandas as pd

from ..backtesting.engine import BacktestConfig
from ..backtesting.walk_forward import run_walk_forward


def run(df: pd.DataFrame, strategy_key: str, cfg: BacktestConfig,
        train_months: int = 24, test_months: int = 6) -> Dict:
    return run_walk_forward(df, strategy_key, cfg, train_months, test_months)
