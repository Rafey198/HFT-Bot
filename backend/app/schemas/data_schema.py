from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DataQualityReport(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    rows: int = 0
    start_date: str = ""
    end_date: str = ""
    missing_candles: int = 0
    duplicate_rows_removed: int = 0
    invalid_rows_removed: int = 0
    data_quality_score: float = 0
    warnings: List[str] = Field(default_factory=list)
    dataset_id: Optional[str] = None
    kind: str = "ohlcv"


class FeatureReport(BaseModel):
    features_created: List[str] = Field(default_factory=list)
    rows_after_feature_engineering: int = 0
    nan_rows_removed: int = 0
    warnings: List[str] = Field(default_factory=list)


class GenerateDemoRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    years: float = 10.0
    kind: str = "ohlcv"  # ohlcv | tick


class DatasetInfo(BaseModel):
    id: str
    symbol: str
    timeframe: str
    kind: str
    rows: int
    start_date: str
    end_date: str
    quality_score: float
    created_at: str
