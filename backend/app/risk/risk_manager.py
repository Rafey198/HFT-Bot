"""Risk manager — overrides all signals. Enforces hard risk caps + kill switch."""
from __future__ import annotations

import time
from collections import deque
from typing import Deque, Dict, List

from ..core.config import DEFAULT_RISK_SETTINGS, symbol_spec
from ..core.logging import get_logger
from .position_sizing import compute_lot_size, reward_risk_ratio

log = get_logger("risk.manager")


class RiskManager:
    """Stateful account-aware risk manager shared by HFT + paper engines."""

    def __init__(self, settings: Dict | None = None):
        self.settings = {**DEFAULT_RISK_SETTINGS, **(settings or {})}
        self.kill_switch_active = False
        self.kill_reason = ""
        self.reset_account()

    def reset_account(self) -> None:
        self.balance = float(self.settings["initial_balance"])
        self.equity = self.balance
        self.day_start_balance = self.balance
        self.week_start_balance = self.balance
        self.peak_equity = self.balance
        self.consecutive_losses = 0
        self.trades_today = 0
        self.open_positions = 0
        self.trade_times: Deque[float] = deque(maxlen=200)
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0

    def update_settings(self, settings: Dict) -> None:
        self.settings.update(settings)

    # --- account events ---------------------------------------------------
    def on_trade_closed(self, pnl: float) -> None:
        self.balance += pnl
        self.daily_pnl += pnl
        self.weekly_pnl += pnl
        self.trades_today += 1
        self.open_positions = max(0, self.open_positions - 1)
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        self._auto_kill_check()

    def on_trade_opened(self) -> None:
        self.open_positions += 1
        self.trade_times.append(time.time())

    def set_equity(self, equity: float) -> None:
        self.equity = equity
        self.peak_equity = max(self.peak_equity, equity)
        self._auto_kill_check()

    # --- kill switch ------------------------------------------------------
    def activate_kill_switch(self, reason: str = "Manual kill switch") -> None:
        self.kill_switch_active = True
        self.kill_reason = reason
        log.warning("KILL SWITCH ACTIVATED: %s", reason)

    def reset_kill_switch(self) -> None:
        self.kill_switch_active = False
        self.kill_reason = ""

    def _auto_kill_check(self) -> None:
        s = self.settings
        daily_loss_pct = -self.daily_pnl / self.day_start_balance * 100 if self.day_start_balance else 0
        dd_pct = (self.peak_equity - self.equity) / self.peak_equity * 100 if self.peak_equity else 0
        if daily_loss_pct >= s["max_daily_loss"]:
            self.activate_kill_switch(f"Max daily loss reached ({daily_loss_pct:.2f}%)")
        elif dd_pct >= s["max_drawdown_stop"]:
            self.activate_kill_switch(f"Max drawdown stop reached ({dd_pct:.2f}%)")

    # --- pre-trade check --------------------------------------------------
    def trades_last_minute(self) -> int:
        now = time.time()
        return sum(1 for t in self.trade_times if now - t <= 60)

    def check(self, signal: Dict, spread_points: float = 0.0) -> Dict:
        s = self.settings
        blocked: List[str] = []

        if self.kill_switch_active:
            blocked.append(f"kill_switch:{self.kill_reason}")

        side = signal.get("side") or signal.get("signal")
        if side not in ("buy", "sell"):
            blocked.append("no_directional_signal")

        entry = float(signal.get("entry") or signal.get("entry_price") or 0)
        sl = float(signal.get("stop_loss") or 0)
        tp = float(signal.get("take_profit") or 0)
        confidence = float(signal.get("confidence") or 0)

        if sl <= 0 or entry <= 0:
            blocked.append("missing_stop_loss")  # never trade without SL
        rr = reward_risk_ratio(entry, sl, tp) if (sl > 0 and entry > 0) else 0
        if rr < s["min_reward_risk"]:
            blocked.append(f"reward_risk_below_min({rr}<{s['min_reward_risk']})")
        if confidence < s["min_signal_confidence"]:
            blocked.append(f"confidence_below_min({confidence}<{s['min_signal_confidence']})")
        if spread_points > s["max_spread_points"]:
            blocked.append(f"spread_too_high({spread_points}>{s['max_spread_points']})")

        if self.open_positions >= s["max_open_positions"]:
            blocked.append("max_open_positions")
        if self.trades_today >= s["max_trades_per_day"]:
            blocked.append("max_trades_per_day")
        if self.trades_last_minute() >= s["max_trades_per_minute"]:
            blocked.append("max_trades_per_minute")
        if self.consecutive_losses >= s["max_consecutive_losses"]:
            blocked.append("max_consecutive_losses")

        daily_loss_pct = -self.daily_pnl / self.day_start_balance * 100 if self.day_start_balance else 0
        if daily_loss_pct >= s["max_daily_loss"]:
            blocked.append("max_daily_loss_reached")
        weekly_loss_pct = -self.weekly_pnl / self.week_start_balance * 100 if self.week_start_balance else 0
        if weekly_loss_pct >= s["max_weekly_loss"]:
            blocked.append("max_weekly_loss_reached")

        symbol = signal.get("symbol", "XAUUSD")
        lot = compute_lot_size(self.balance, s["risk_per_trade"], entry, sl, symbol) if sl > 0 and entry > 0 else 0

        allowed = len(blocked) == 0 and lot > 0
        status = "safe"
        if blocked:
            status = "blocked"
        elif self.consecutive_losses >= max(1, s["max_consecutive_losses"] - 1) or daily_loss_pct > s["max_daily_loss"] * 0.6:
            status = "warning"

        return {
            "trade_allowed": allowed,
            "lot_size": lot,
            "risk_percent": s["risk_per_trade"],
            "blocked_by": blocked,
            "risk_status": status,
        }

    def state(self) -> Dict:
        s = self.settings
        daily_loss_pct = -self.daily_pnl / self.day_start_balance * 100 if self.day_start_balance else 0
        dd_pct = (self.peak_equity - self.equity) / self.peak_equity * 100 if self.peak_equity else 0
        return {
            "balance": round(self.balance, 2),
            "equity": round(self.equity, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "daily_pnl_percent": round(self.daily_pnl / self.day_start_balance * 100, 3) if self.day_start_balance else 0,
            "weekly_pnl": round(self.weekly_pnl, 2),
            "drawdown_percent": round(dd_pct, 2),
            "max_daily_loss": s["max_daily_loss"],
            "max_drawdown_stop": s["max_drawdown_stop"],
            "consecutive_losses": self.consecutive_losses,
            "open_positions": self.open_positions,
            "trades_today": self.trades_today,
            "trades_per_minute": self.trades_last_minute(),
            "max_trades_per_minute": s["max_trades_per_minute"],
            "kill_switch_active": self.kill_switch_active,
            "kill_reason": self.kill_reason,
            "auto_disabled": self.kill_switch_active,
            "risk_status": "blocked" if self.kill_switch_active else ("warning" if daily_loss_pct > s["max_daily_loss"] * 0.6 else "safe"),
        }
