"""Safety agent — audits strategies, metrics, and system state before live use."""
from __future__ import annotations

from typing import Dict, List, Optional


def audit_backtest(result: Dict) -> Dict:
    warnings: List[str] = []
    must_fix: List[str] = []

    win_rate = result.get("win_rate", 0)
    pf = result.get("profit_factor", 0)
    dd = result.get("max_drawdown", 0)
    trades = result.get("num_trades", 0)
    sharpe = result.get("sharpe", 0)

    if win_rate > 85 and trades > 0:
        warnings.append("Win rate >85% is unrealistic — suspect overfitting or look-ahead bias.")
    if trades < 20:
        warnings.append("Too few trades to validate edge statistically.")
    if dd > 30:
        warnings.append(f"High max drawdown ({dd}%) — risky for live capital.")
    if pf > 5 and trades > 0:
        warnings.append("Profit factor >5 is suspicious — re-check data leakage.")
    if sharpe > 5:
        warnings.append("Sharpe >5 is implausible for retail FX — likely overfit.")

    return {"warnings": warnings, "must_fix_before_live": must_fix}


def audit_system(live_mode: bool, has_paper_record: bool, risk_settings: Dict,
                 broker_connected: bool, kill_switch_visible: bool = True,
                 best_backtest: Optional[Dict] = None) -> Dict:
    warnings: List[str] = []
    must_fix: List[str] = []

    if risk_settings.get("risk_per_trade", 1) > 1.0:
        warnings.append("Risk per trade above 1% is aggressive for HFT-style scalping.")
    if risk_settings.get("max_daily_loss", 0) > 5:
        warnings.append("Max daily loss above 5% is dangerous.")
    if risk_settings.get("max_open_positions", 0) > 5:
        warnings.append("Many simultaneous positions increases correlated risk.")
    if risk_settings.get("min_reward_risk", 0) < 1.0:
        warnings.append("Minimum reward:risk below 1.0 — negative expectancy risk.")

    if live_mode and not has_paper_record:
        must_fix.append("Paper trading record required before enabling live mode.")
    if live_mode and not broker_connected:
        must_fix.append("Broker connection must be verified before live mode.")
    if not kill_switch_visible:
        must_fix.append("Kill switch must be visible before live mode.")

    if best_backtest:
        sub = audit_backtest(best_backtest)
        warnings += sub["warnings"]

    system_safe = len(must_fix) == 0
    return {
        "system_safe": system_safe,
        "warnings": warnings,
        "must_fix_before_live": must_fix,
    }
