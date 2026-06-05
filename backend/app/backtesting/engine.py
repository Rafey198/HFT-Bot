"""Realistic event-driven backtester (no look-ahead, spread/slippage/commission)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from ..core.config import symbol_spec
from ..core.logging import get_logger
from ..features.pipeline import build_features
from ..strategies.base import Strategy
from ..strategies.registry import get_strategy
from . import metrics as M

log = get_logger("backtest.engine")

CONTRACT_SIZE = {
    "XAUUSD": 100.0,
    "EURUSD": 100000.0, "GBPUSD": 100000.0, "USDJPY": 100000.0,
    "USDCHF": 100000.0, "AUDUSD": 100000.0, "USDCAD": 100000.0, "NZDUSD": 100000.0,
}

BARS_PER_YEAR = {
    "M1": 525600, "M5": 105120, "M15": 35040, "M30": 17520,
    "H1": 8760, "H4": 2190, "D1": 365,
}


@dataclass
class BacktestConfig:
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    initial_balance: float = 10000
    risk_per_trade: float = 0.25
    spread_points: float = 20
    commission_per_lot: float = 7.0
    slippage_points: float = 2.0
    max_open_trades: int = 2
    use_trailing_stop: bool = False
    min_reward_risk: float = 0.0


@dataclass
class _OpenPos:
    side: int
    entry_price: float
    sl: float
    tp: float
    lot: float
    entry_idx: int
    entry_time: str
    risk_amount: float
    trail: float = 0.0


def run_backtest(df: pd.DataFrame, strategy: Strategy, cfg: BacktestConfig,
                 with_curves: bool = True, max_trades_keep: int = 500) -> Dict:
    """Run a single-strategy backtest. df must already have features."""
    spec = symbol_spec(cfg.symbol)
    point = spec["point"]
    contract = CONTRACT_SIZE.get(cfg.symbol.upper(), 100000.0)
    spread_price = cfg.spread_points * point
    slip_price = cfg.slippage_points * point

    dirs = strategy.directions(df).to_numpy()
    open_ = df["open"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    close = df["close"].to_numpy()
    atr = df["atr"].to_numpy() if "atr" in df.columns else close * 0.001
    ts = df["timestamp"].astype(str).to_numpy()

    balance = cfg.initial_balance
    equity = balance
    open_positions: List[_OpenPos] = []
    trades: List[Dict] = []
    equity_curve: List[Dict] = []

    n = len(df)
    for i in range(n - 1):
        # 1) Manage open positions on bar i (intrabar SL/TP using high/low).
        still_open: List[_OpenPos] = []
        for pos in open_positions:
            exit_price = None
            reason = ""
            # trailing stop update
            if cfg.use_trailing_stop:
                a = max(atr[i], close[i] * 1e-5)
                if pos.side > 0:
                    pos.trail = max(pos.trail, close[i] - 1.5 * a)
                    pos.sl = max(pos.sl, pos.trail)
                else:
                    pos.trail = min(pos.trail or 1e18, close[i] + 1.5 * a)
                    pos.sl = min(pos.sl, pos.trail)
            if pos.side > 0:
                if low[i] <= pos.sl:
                    exit_price = pos.sl - slip_price
                    reason = "stop_loss"
                elif high[i] >= pos.tp:
                    exit_price = pos.tp - slip_price
                    reason = "take_profit"
            else:
                if high[i] >= pos.sl:
                    exit_price = pos.sl + slip_price
                    reason = "stop_loss"
                elif low[i] <= pos.tp:
                    exit_price = pos.tp + slip_price
                    reason = "take_profit"

            if exit_price is not None:
                pnl = (exit_price - pos.entry_price) * pos.side * contract * pos.lot
                commission = cfg.commission_per_lot * pos.lot * 2
                pnl -= commission
                balance += pnl
                trades.append({
                    "trade_id": f"bt_{len(trades)+1}",
                    "symbol": cfg.symbol, "side": "buy" if pos.side > 0 else "sell",
                    "entry_time": pos.entry_time, "entry_price": round(pos.entry_price, 5),
                    "stop_loss": round(pos.sl, 5), "take_profit": round(pos.tp, 5),
                    "exit_time": ts[i], "exit_price": round(exit_price, 5),
                    "lot_size": round(pos.lot, 3), "pnl": round(pnl, 2),
                    "pnl_percent": round(pnl / cfg.initial_balance * 100, 3),
                    "status": "closed", "strategy": strategy.name, "reason": reason,
                    "hold_bars": i - pos.entry_idx,
                })
            else:
                still_open.append(pos)
        open_positions = still_open

        # 2) Mark-to-market equity (always tracked; needed for metrics).
        unrealized = 0.0
        for pos in open_positions:
            unrealized += (close[i] - pos.entry_price) * pos.side * contract * pos.lot
        equity = balance + unrealized
        equity_curve.append({"t": ts[i], "equity": round(equity, 2)})

        # 3) New entry on signal at bar i -> fill at bar i+1 open (no look-ahead).
        sig = int(dirs[i])
        if sig != 0 and len(open_positions) < cfg.max_open_trades:
            fill_idx = i + 1
            raw_fill = open_[fill_idx]
            if sig > 0:
                entry_price = raw_fill + spread_price / 2 + slip_price
            else:
                entry_price = raw_fill - spread_price / 2 - slip_price
            a = max(atr[i], close[i] * 1e-5)
            sl = entry_price - strategy.sl_atr * a if sig > 0 else entry_price + strategy.sl_atr * a
            tp = entry_price + strategy.tp_atr * a if sig > 0 else entry_price - strategy.tp_atr * a
            sl_dist = abs(entry_price - sl)
            rr = abs(tp - entry_price) / sl_dist if sl_dist > 0 else 0
            if sl_dist <= 0 or (cfg.min_reward_risk and rr < cfg.min_reward_risk):
                continue
            risk_amount = balance * cfg.risk_per_trade / 100.0
            lot = risk_amount / (sl_dist * contract)
            lot = float(np.clip(lot, 0.0, 100.0))
            if lot <= 0:
                continue
            open_positions.append(_OpenPos(
                side=sig, entry_price=entry_price, sl=sl, tp=tp, lot=lot,
                entry_idx=fill_idx, entry_time=ts[fill_idx], risk_amount=risk_amount,
                trail=0.0,
            ))

    # Final equity point.
    equity_curve.append({"t": ts[-1], "equity": round(balance, 2)})

    bpy = BARS_PER_YEAR.get(cfg.timeframe, 105120)
    stats = M.compute_metrics(trades, equity_curve, cfg.initial_balance, n, bpy)

    warnings: List[str] = []
    if stats["num_trades"] < 15:
        warnings.append("Low trade count — results not statistically reliable.")
    if stats["win_rate"] > 80:
        warnings.append("Unusually high win rate — check for overfitting/look-ahead.")
    if stats["max_drawdown"] > 35:
        warnings.append("High max drawdown — risky for live capital.")

    # Drawdown curve.
    dd_curve: List[Dict] = []
    if with_curves and equity_curve:
        eq = pd.DataFrame(equity_curve)
        roll = eq["equity"].cummax()
        dd = (eq["equity"] - roll) / roll * 100
        dd_curve = [{"t": t, "drawdown": round(float(d), 2)}
                    for t, d in zip(eq["t"], dd)]

    result = {
        "strategy_name": strategy.name,
        "symbol": cfg.symbol,
        "timeframe": cfg.timeframe,
        **stats,
        "recommendation": M.recommendation(stats),
        "warnings": warnings,
        "equity_curve": _downsample(equity_curve, 800) if with_curves else [],
        "drawdown_curve": _downsample(dd_curve, 800) if with_curves else [],
        "monthly_returns": M.monthly_returns(equity_curve) if with_curves else [],
        "yearly_returns": M.yearly_returns(equity_curve) if with_curves else [],
        "trades": trades[-max_trades_keep:],
    }
    return result


def _downsample(series: List[Dict], target: int) -> List[Dict]:
    if len(series) <= target:
        return series
    step = max(1, len(series) // target)
    return series[::step]


def run_backtest_by_key(df: pd.DataFrame, strategy_key: str, cfg: BacktestConfig,
                        params: Optional[Dict] = None, **kwargs) -> Dict:
    if not {"atr", "ema_200"}.issubset(df.columns):
        df, _ = build_features(df)
    strat = get_strategy(strategy_key, params)
    return run_backtest(df, strat, cfg, **kwargs)
