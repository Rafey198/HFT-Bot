"""Walk-forward validation: rolling train/test windows on out-of-sample data."""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from ..core.logging import get_logger
from ..features.pipeline import build_features
from ..strategies.registry import get_strategy
from .engine import BacktestConfig, run_backtest

log = get_logger("backtest.walk_forward")


def run_walk_forward(df: pd.DataFrame, strategy_key: str, cfg: BacktestConfig,
                     train_months: int = 24, test_months: int = 6,
                     param_grid: Optional[List[Dict]] = None) -> Dict:
    if not {"atr", "ema_200"}.issubset(df.columns):
        df, _ = build_features(df)
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    start = df["timestamp"].iloc[0]
    end = df["timestamp"].iloc[-1]

    # Adapt window sizes if the dataset span is too short for the requested split.
    span_days = max(1.0, (end - start).total_seconds() / 86400.0)
    span_months = span_days / 30.4
    if span_months < train_months + 2 * test_months:
        train_months = max(1, int(span_months * 0.5))
        test_months = max(1, int(span_months * 0.15))

    train_delta = pd.DateOffset(months=train_months)
    test_delta = pd.DateOffset(months=test_months)

    if param_grid is None:
        base = get_strategy(strategy_key)
        param_grid = _default_grid(strategy_key, base.params)

    windows: List[Dict] = []
    cursor = start
    while True:
        train_end = cursor + train_delta
        test_end = train_end + test_delta
        if train_end >= end:
            break
        train = df[(df["timestamp"] >= cursor) & (df["timestamp"] < train_end)]
        test = df[(df["timestamp"] >= train_end) & (df["timestamp"] < test_end)]
        if len(train) < 300 or len(test) < 100:
            cursor = cursor + test_delta
            if cursor >= end:
                break
            continue

        # Optimize params on TRAIN only.
        best_params, best_score = None, -1e18
        for params in param_grid:
            strat = get_strategy(strategy_key, params)
            res = run_backtest(train.reset_index(drop=True), strat, cfg, with_curves=False)
            score = res["expectancy"] * np.sqrt(max(res["num_trades"], 0)) + res["profit_factor"]
            if score > best_score:
                best_score, best_params = score, params

        # Evaluate on unseen TEST.
        strat = get_strategy(strategy_key, best_params)
        oos = run_backtest(test.reset_index(drop=True), strat, cfg, with_curves=False)
        windows.append({
            "train_start": str(cursor.date()),
            "train_end": str(train_end.date()),
            "test_start": str(train_end.date()),
            "test_end": str(test_end.date()),
            "params": best_params,
            "oos_return": oos["total_return"],
            "oos_drawdown": oos["max_drawdown"],
            "oos_profit_factor": oos["profit_factor"],
            "oos_trades": oos["num_trades"],
            "oos_win_rate": oos["win_rate"],
        })
        cursor = cursor + test_delta
        if cursor + train_delta >= end:
            break

    if not windows:
        return {
            "windows": [], "average_oos_return": 0, "average_oos_drawdown": 0,
            "average_oos_profit_factor": 0, "stability_score": 0,
            "overfitting_warning": True,
            "recommendation": "Insufficient data for walk-forward validation.",
        }

    rets = np.array([w["oos_return"] for w in windows])
    dds = np.array([w["oos_drawdown"] for w in windows])
    pfs = np.array([w["oos_profit_factor"] for w in windows])

    avg_ret = float(rets.mean())
    avg_dd = float(dds.mean())
    avg_pf = float(pfs.mean())
    positive_frac = float((rets > 0).mean())
    consistency = 1.0 - min(1.0, rets.std() / (abs(avg_ret) + 1e-6))
    stability = round(max(0.0, min(100.0, (positive_frac * 60 + consistency * 40))), 1)

    overfit = stability < 45 or avg_pf < 1.0 or positive_frac < 0.5
    rec = _recommend(stability, avg_pf, positive_frac)

    return {
        "windows": windows,
        "average_oos_return": round(avg_ret, 2),
        "average_oos_drawdown": round(avg_dd, 2),
        "average_oos_profit_factor": round(avg_pf, 2),
        "stability_score": stability,
        "overfitting_warning": bool(overfit),
        "recommendation": rec,
    }


def _default_grid(key: str, base: Dict) -> List[Dict]:
    grids = {
        "ema_crossover": [{"fast": 9, "slow": 21}, {"fast": 12, "slow": 26}, {"fast": 5, "slow": 20}],
        "sma_crossover": [{"fast": 20, "slow": 50}, {"fast": 10, "slow": 40}, {"fast": 30, "slow": 100}],
        "rsi_reversal": [{"low": 30, "high": 70}, {"low": 25, "high": 75}, {"low": 35, "high": 65}],
        "atr_breakout": [{"mult": 0.8}, {"mult": 1.0}, {"mult": 1.5}],
        "adx_trend_strength": [{"adx_min": 20}, {"adx_min": 25}, {"adx_min": 30}],
    }
    return grids.get(key, [base or {}])


def _recommend(stability: float, pf: float, positive_frac: float) -> str:
    if stability >= 60 and pf >= 1.2 and positive_frac >= 0.6:
        return "Robust out-of-sample — candidate for paper trading."
    if stability >= 45 and pf >= 1.0:
        return "Marginal robustness — paper test with caution."
    return "Likely overfit — reject for live use."
