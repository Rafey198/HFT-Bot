"""Backtest agent — runs single + batch backtests."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from ..backtesting.engine import BacktestConfig, run_backtest
from ..features.pipeline import build_features
from ..strategies.registry import all_keys, get_strategy


def _ensure_features(df: pd.DataFrame) -> pd.DataFrame:
    if not {"atr", "ema_200"}.issubset(df.columns):
        df, _ = build_features(df)
    return df


def run_one(df: pd.DataFrame, strategy_key: str, cfg: BacktestConfig,
            params: Optional[Dict] = None) -> Dict:
    df = _ensure_features(df)
    strat = get_strategy(strategy_key, params)
    res = run_backtest(df, strat, cfg)
    res["strategy_key"] = strategy_key
    return res


def run_all(df: pd.DataFrame, cfg: BacktestConfig, keys: Optional[List[str]] = None,
            max_bars: int = 60000) -> List[Dict]:
    df = _ensure_features(df)
    if len(df) > max_bars:
        df = df.tail(max_bars).reset_index(drop=True)
    keys = keys or all_keys()
    results = []
    for key in keys:
        try:
            strat = get_strategy(key)
            res = run_backtest(df, strat, cfg, with_curves=False, max_trades_keep=0)
            res["strategy_key"] = key
            res.pop("trades", None)
            results.append(res)
        except Exception as exc:  # noqa: BLE001
            results.append({"strategy_key": key, "strategy_name": key,
                            "error": str(exc), "num_trades": 0, "recommendation": "reject"})
    results.sort(key=lambda r: (r.get("profit_factor", 0), r.get("total_return", 0)), reverse=True)
    return results
