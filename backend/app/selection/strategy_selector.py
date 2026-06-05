"""Strategy selection agent — combines regime fit + robustness metrics."""
from __future__ import annotations

from typing import Dict, List, Optional

from ..regimes.regime_detector import detect_regime
from ..strategies.registry import REGISTRY


def _score(metrics: Dict, regime_fit: float) -> float:
    """Composite score. Deliberately NOT based on win rate alone."""
    pf = metrics.get("profit_factor", 0) or 0
    dd = metrics.get("max_drawdown", 100) or 100
    expectancy = metrics.get("expectancy", 0) or 0
    trades = metrics.get("num_trades", 0) or 0
    stability = metrics.get("stability_score", 50) or 50
    if trades < 10:
        return -100.0
    score = 0.0
    score += min(pf, 3.0) * 20
    score += max(-1.0, expectancy / 50.0) * 10
    score -= dd * 0.5
    score += stability * 0.4
    score += regime_fit * 15
    score += min(trades / 50.0, 1.0) * 5
    return round(score, 2)


def select_strategy(df, results: List[Dict],
                    stability_by_key: Optional[Dict[str, float]] = None) -> Dict:
    """results: list of backtest result dicts with a 'strategy_key' field."""
    regime = detect_regime(df)
    rec_types = set(regime["recommended_strategy_types"])
    avoid_types = set(regime["avoid_strategy_types"])
    stability_by_key = stability_by_key or {}

    ranked = []
    for r in results:
        key = r.get("strategy_key") or r.get("key")
        cls = REGISTRY.get(key)
        cat = cls.category if cls else "generic"
        regime_fit = 1.0 if cat in rec_types else (-1.0 if cat in avoid_types else 0.0)
        merged = dict(r)
        merged["stability_score"] = stability_by_key.get(key, r.get("stability_score", 50))
        s = _score(merged, regime_fit)
        ranked.append((s, key, cat, r))

    ranked.sort(key=lambda x: x[0], reverse=True)
    if not ranked or ranked[0][0] < 0:
        return {
            "selected_strategy": "",
            "backup_strategy": "",
            "reason": f"No strategy passes robustness thresholds in the current "
                      f"'{regime['regime']}' regime.",
            "risk_warning": "Stand aside — insufficient edge. Do not force trades.",
            "confidence": round(regime["confidence"] * 0.4, 1),
        }

    best = ranked[0]
    backup = ranked[1] if len(ranked) > 1 else None
    risk_warning = ""
    if best[3].get("max_drawdown", 0) > 25:
        risk_warning = "Selected strategy has elevated drawdown — size down."
    if best[2] in avoid_types:
        risk_warning = (risk_warning + " Category is disfavoured by current regime.").strip()

    return {
        "selected_strategy": best[1],
        "backup_strategy": backup[1] if backup else "",
        "reason": (f"Best composite score {best[0]} in '{regime['regime']}' regime "
                   f"(profit factor {best[3].get('profit_factor')}, DD "
                   f"{best[3].get('max_drawdown')}%). Category '{best[2]}' fit."),
        "risk_warning": risk_warning or "Standard risk caps apply.",
        "confidence": round(min(95.0, max(35.0, regime["confidence"] * 0.6 + best[0] * 0.2)), 1),
    }
