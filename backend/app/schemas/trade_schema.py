from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    strategy_key: str = "ema_crossover"
    dataset_id: Optional[str] = None
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    initial_balance: float = 10000
    risk_per_trade: float = 0.25
    spread_points: float = 20
    commission_per_lot: float = 7.0
    slippage_points: float = 2.0
    max_open_trades: int = 2
    use_trailing_stop: bool = False
    parameters: dict = Field(default_factory=dict)


class RunAllRequest(BacktestRequest):
    strategy_key: str = ""
    top_n: int = 35


class BacktestResult(BaseModel):
    strategy_name: str = ""
    symbol: str = ""
    timeframe: str = ""
    total_return: float = 0
    cagr: float = 0
    win_rate: float = 0
    profit_factor: float = 0
    expectancy: float = 0
    max_drawdown: float = 0
    sharpe: float = 0
    sortino: float = 0
    calmar: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    avg_hold_time: float = 0
    risk_reward: float = 0
    longest_losing_streak: int = 0
    num_trades: int = 0
    exposure_time: float = 0
    recommendation: str = "reject"
    warnings: List[str] = Field(default_factory=list)
    equity_curve: List[dict] = Field(default_factory=list)
    drawdown_curve: List[dict] = Field(default_factory=list)
    monthly_returns: List[dict] = Field(default_factory=list)
    yearly_returns: List[dict] = Field(default_factory=list)
    trades: List[dict] = Field(default_factory=list)


class WalkForwardRequest(BacktestRequest):
    train_months: int = 24
    test_months: int = 6


class WalkForwardResult(BaseModel):
    windows: List[dict] = Field(default_factory=list)
    average_oos_return: float = 0
    average_oos_drawdown: float = 0
    average_oos_profit_factor: float = 0
    stability_score: float = 0
    overfitting_warning: bool = False
    recommendation: str = ""
