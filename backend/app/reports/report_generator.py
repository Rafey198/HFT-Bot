"""Report generator — assembles backtest / paper summaries."""
from __future__ import annotations

from typing import Dict, List

from ..core.config import DISCLAIMER
from ..core.utils import now_iso


def backtest_report(result: Dict) -> Dict:
    return {
        "title": f"Backtest Report — {result.get('strategy_name', '')} {result.get('symbol', '')} {result.get('timeframe', '')}",
        "generated_at": now_iso(),
        "disclaimer": DISCLAIMER,
        "summary": {
            "total_return": result.get("total_return"),
            "cagr": result.get("cagr"),
            "max_drawdown": result.get("max_drawdown"),
            "profit_factor": result.get("profit_factor"),
            "sharpe": result.get("sharpe"),
            "win_rate": result.get("win_rate"),
            "num_trades": result.get("num_trades"),
            "recommendation": result.get("recommendation"),
        },
        "sections": [
            {"heading": "Risk-adjusted performance", "metrics": {
                "sharpe": result.get("sharpe"), "sortino": result.get("sortino"),
                "calmar": result.get("calmar"), "expectancy": result.get("expectancy"),
            }},
            {"heading": "Trade statistics", "metrics": {
                "avg_win": result.get("avg_win"), "avg_loss": result.get("avg_loss"),
                "risk_reward": result.get("risk_reward"),
                "longest_losing_streak": result.get("longest_losing_streak"),
                "exposure_time": result.get("exposure_time"),
            }},
            {"heading": "Warnings", "items": result.get("warnings", [])},
        ],
    }


def paper_report(broker_state: Dict, risk_state: Dict, trades: List[Dict]) -> Dict:
    wins = [t for t in trades if t.get("pnl", 0) > 0]
    return {
        "title": "Paper Trading Report",
        "generated_at": now_iso(),
        "disclaimer": DISCLAIMER,
        "summary": {
            "balance": broker_state.get("balance"),
            "equity": broker_state.get("equity"),
            "open_positions": broker_state.get("open_count"),
            "closed_trades": broker_state.get("closed_count"),
            "win_rate": round(len(wins) / len(trades) * 100, 2) if trades else 0,
            "daily_pnl": risk_state.get("daily_pnl"),
            "drawdown_percent": risk_state.get("drawdown_percent"),
            "kill_switch_active": risk_state.get("kill_switch_active"),
        },
        "sections": [
            {"heading": "Risk state", "metrics": risk_state},
        ],
    }
