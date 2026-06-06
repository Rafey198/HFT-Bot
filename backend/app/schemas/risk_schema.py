from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class RiskSettings(BaseModel):
    initial_balance: float = 10000
    risk_per_trade: float = 0.25
    max_daily_loss: float = 2.0
    max_weekly_loss: float = 5.0
    max_drawdown_stop: float = 10.0
    max_trades_per_minute: int = 5
    max_trades_per_day: int = 50
    max_consecutive_losses: int = 3
    max_open_positions: int = 2
    min_reward_risk: float = 1.2
    max_spread_points: float = 30
    min_signal_confidence: float = 60


class RiskCheckResult(BaseModel):
    trade_allowed: bool = True
    lot_size: float = 0
    risk_percent: float = 0
    blocked_by: List[str] = Field(default_factory=list)
    risk_status: str = "safe"  # safe | warning | blocked


class SafetyReport(BaseModel):
    system_safe: bool = True
    warnings: List[str] = Field(default_factory=list)
    must_fix_before_live: List[str] = Field(default_factory=list)
