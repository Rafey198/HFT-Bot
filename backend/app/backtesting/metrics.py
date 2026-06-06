"""Performance metrics from a list of closed trades + equity curve."""
from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
import pandas as pd


def _safe(v, default=0.0):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return default
    return v


def compute_metrics(trades: List[Dict], equity_curve: List[Dict],
                    initial_balance: float, total_bars: int,
                    bars_per_year: float) -> Dict:
    n = len(trades)
    if n == 0 or len(equity_curve) < 2:
        return {
            "total_return": 0, "cagr": 0, "win_rate": 0, "profit_factor": 0,
            "expectancy": 0, "max_drawdown": 0, "sharpe": 0, "sortino": 0,
            "calmar": 0, "avg_win": 0, "avg_loss": 0, "avg_hold_time": 0,
            "risk_reward": 0, "longest_losing_streak": 0, "num_trades": 0,
            "exposure_time": 0,
        }

    eq = pd.DataFrame(equity_curve)
    eq["equity"] = pd.to_numeric(eq["equity"], errors="coerce").ffill()
    final_equity = float(eq["equity"].iloc[-1])
    total_return = (final_equity / initial_balance - 1) * 100

    pnls = np.array([t["pnl"] for t in trades], dtype=float)
    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]
    win_rate = len(wins) / n * 100
    gross_win = wins.sum()
    gross_loss = -losses.sum()
    profit_factor = gross_win / gross_loss if gross_loss > 0 else (gross_win and 99.0)
    avg_win = wins.mean() if len(wins) else 0.0
    avg_loss = losses.mean() if len(losses) else 0.0
    expectancy = pnls.mean()
    risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0.0

    # Returns series for ratios (per-bar equity returns).
    eq_ret = eq["equity"].pct_change().dropna()
    ann = bars_per_year
    if eq_ret.std() > 0:
        sharpe = eq_ret.mean() / eq_ret.std() * math.sqrt(ann)
    else:
        sharpe = 0.0
    downside = eq_ret[eq_ret < 0]
    if downside.std() > 0:
        sortino = eq_ret.mean() / downside.std() * math.sqrt(ann)
    else:
        sortino = 0.0

    roll_max = eq["equity"].cummax()
    dd = (eq["equity"] - roll_max) / roll_max
    max_dd = abs(dd.min()) * 100

    years = max(total_bars / bars_per_year, 1e-6)
    cagr = ((final_equity / initial_balance) ** (1 / years) - 1) * 100 if final_equity > 0 else -100
    calmar = cagr / max_dd if max_dd > 0 else 0.0

    # Hold time + losing streak.
    holds = [t.get("hold_bars", 0) for t in trades]
    avg_hold = float(np.mean(holds)) if holds else 0.0
    streak = longest = 0
    for p in pnls:
        if p < 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0

    exposure = sum(holds) / total_bars * 100 if total_bars else 0.0

    return {
        "total_return": round(_safe(total_return), 2),
        "cagr": round(_safe(cagr), 2),
        "win_rate": round(_safe(win_rate), 2),
        "profit_factor": round(_safe(profit_factor), 2),
        "expectancy": round(_safe(expectancy), 2),
        "max_drawdown": round(_safe(max_dd), 2),
        "sharpe": round(_safe(sharpe), 2),
        "sortino": round(_safe(sortino), 2),
        "calmar": round(_safe(calmar), 2),
        "avg_win": round(_safe(avg_win), 2),
        "avg_loss": round(_safe(avg_loss), 2),
        "avg_hold_time": round(_safe(avg_hold), 1),
        "risk_reward": round(_safe(risk_reward), 2),
        "longest_losing_streak": int(longest),
        "num_trades": n,
        "exposure_time": round(_safe(exposure), 1),
    }


def monthly_returns(equity_curve: List[Dict]) -> List[Dict]:
    if len(equity_curve) < 2:
        return []
    eq = pd.DataFrame(equity_curve)
    eq["t"] = pd.to_datetime(eq["t"], utc=True, errors="coerce")
    eq = eq.dropna(subset=["t"]).set_index("t")
    monthly = eq["equity"].resample("ME").last().dropna()
    rets = monthly.pct_change().dropna() * 100
    return [{"month": idx.strftime("%Y-%m"), "return": round(float(v), 2)}
            for idx, v in rets.items()]


def yearly_returns(equity_curve: List[Dict]) -> List[Dict]:
    if len(equity_curve) < 2:
        return []
    eq = pd.DataFrame(equity_curve)
    eq["t"] = pd.to_datetime(eq["t"], utc=True, errors="coerce")
    eq = eq.dropna(subset=["t"]).set_index("t")
    yearly = eq["equity"].resample("YE").last().dropna()
    rets = yearly.pct_change().dropna() * 100
    return [{"year": idx.strftime("%Y"), "return": round(float(v), 2)}
            for idx, v in rets.items()]


def recommendation(metrics: Dict) -> str:
    pf = metrics.get("profit_factor", 0)
    dd = metrics.get("max_drawdown", 100)
    trades = metrics.get("num_trades", 0)
    expectancy = metrics.get("expectancy", 0)
    if trades < 15:
        return "reject"
    if pf >= 1.4 and dd <= 25 and expectancy > 0:
        return "candidate"
    if pf >= 1.1 and dd <= 35 and expectancy > 0:
        return "paper_test"
    return "reject"
