"""Strategy library agent."""
from __future__ import annotations

from typing import Dict, List

from ..strategies.registry import category_map, list_strategy_info


def list_all() -> List[Dict]:
    return list_strategy_info()


def categories() -> Dict[str, List[str]]:
    return category_map()
