"""Explainability agent — plain-English rationale for signals / trades."""
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


def _vote(name: str, value, condition: bool, note: str) -> Dict:
    return {"indicator": name, "value": value, "agrees": bool(condition), "note": note}


def explain_signal(signal: Dict, row: Optional[Dict] = None, regime: str = "",
                   risk_check: Optional[Dict] = None) -> Dict:
    side = signal.get("side") or signal.get("signal", "hold")
    votes: List[Dict] = []
    if row:
        rsi = row.get("rsi")
        adx = row.get("adx")
        macd_hist = row.get("macd_hist")
        if rsi is not None:
            votes.append(_vote("RSI", round(rsi, 1),
                               (side == "buy" and rsi < 50) or (side == "sell" and rsi > 50),
                               "Momentum bias relative to 50."))
        if adx is not None:
            votes.append(_vote("ADX", round(adx, 1), adx > 20, "Trend strength filter."))
        if macd_hist is not None:
            votes.append(_vote("MACD hist", round(macd_hist, 4),
                               (side == "buy" and macd_hist > 0) or (side == "sell" and macd_hist < 0),
                               "MACD momentum alignment."))

    entry = signal.get("entry") or signal.get("entry_price", 0)
    sl = signal.get("stop_loss", 0)
    tp = signal.get("take_profit", 0)
    risk_notes: List[str] = []
    if sl and entry:
        risk_notes.append(f"Stop loss placed {abs(entry - sl):.5f} away (ATR-based volatility buffer).")
    if tp and entry and sl:
        rr = abs(tp - entry) / max(abs(entry - sl), 1e-9)
        risk_notes.append(f"Reward:risk ≈ {rr:.2f}.")
    if risk_check:
        risk_notes.append(f"Risk manager status: {risk_check.get('risk_status')}, "
                          f"lot {risk_check.get('lot_size')}.")
        if risk_check.get("blocked_by"):
            risk_notes.append("Blocked by: " + ", ".join(risk_check["blocked_by"]))

    what_could_go_wrong = [
        "Spread widening or slippage can erode a tight scalping edge.",
        "News-driven volatility spikes can blow through the stop.",
        "Regime can shift; a trend signal fails in choppy markets.",
        "Past performance does not guarantee future results.",
    ]

    plain = (
        f"{signal.get('strategy', 'Strategy')} produced a {side.upper()} signal on "
        f"{signal.get('symbol', '')}. Detected regime: {regime or 'n/a'}. "
        f"Confidence {signal.get('confidence', 0)}. {signal.get('reason', '')}"
    )
    return {
        "plain_english_reason": plain.strip(),
        "indicator_votes": votes,
        "risk_notes": risk_notes,
        "what_could_go_wrong": what_could_go_wrong,
    }
