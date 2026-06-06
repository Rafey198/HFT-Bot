"""Broker interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


class BrokerBase(ABC):
    name = "base"
    is_live = False

    @abstractmethod
    def connect(self) -> Dict:
        ...

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict:
        ...

    @abstractmethod
    def place_order(self, order: Dict) -> Dict:
        ...

    @abstractmethod
    def close_order(self, trade_id: str, price: float, reason: str = "manual") -> Dict:
        ...

    @abstractmethod
    def open_positions(self) -> List[Dict]:
        ...
