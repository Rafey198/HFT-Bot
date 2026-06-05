from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class RegimeResult(BaseModel):
    regime: str = "ranging"
    confidence: float = 0
    recommended_strategy_types: List[str] = Field(default_factory=list)
    avoid_strategy_types: List[str] = Field(default_factory=list)
    reason: str = ""


class StrategySelection(BaseModel):
    selected_strategy: str = ""
    backup_strategy: str = ""
    reason: str = ""
    risk_warning: str = ""
    confidence: float = 0


class Explanation(BaseModel):
    plain_english_reason: str = ""
    indicator_votes: List[Dict[str, Any]] = Field(default_factory=list)
    risk_notes: List[str] = Field(default_factory=list)
    what_could_go_wrong: List[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    title: str
    generated_at: str
    summary: Dict[str, Any] = Field(default_factory=dict)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
