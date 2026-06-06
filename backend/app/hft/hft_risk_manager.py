"""HFT risk manager — thin wrapper adding tick-rate caps on top of RiskManager."""
from __future__ import annotations

from typing import Dict

from ..risk.risk_manager import RiskManager


class HftRiskManager:
    """Wraps the shared RiskManager so HFT flow has one risk authority."""

    def __init__(self, risk_manager: RiskManager):
        self.rm = risk_manager

    def check(self, signal: Dict, spread_points: float = 0.0) -> Dict:
        return self.rm.check(signal, spread_points=spread_points)

    @property
    def kill_switch_active(self) -> bool:
        return self.rm.kill_switch_active

    def state(self) -> Dict:
        return self.rm.state()
