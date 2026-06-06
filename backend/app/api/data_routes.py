from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..core.config import (PRIMARY_SYMBOL, SUPPORTED_SYMBOLS,
                          SUPPORTED_TIMEFRAMES)
from ..core.database import get_dataset, list_datasets
from ..data import ingestion
from ..features.pipeline import build_features
from ..schemas.data_schema import GenerateDemoRequest

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/symbols")
def symbols():
    return {"symbols": SUPPORTED_SYMBOLS, "primary": PRIMARY_SYMBOL,
            "timeframes": SUPPORTED_TIMEFRAMES}


@router.post("/upload")
async def upload(file: UploadFile = File(...), symbol: str = Form(PRIMARY_SYMBOL),
                 timeframe: str = Form("")):
    content = await file.read()
    try:
        report = ingestion.ingest_csv(content, symbol, timeframe or None)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {exc}")
    return report


@router.post("/generate-demo")
def generate_demo(req: GenerateDemoRequest):
    return ingestion.generate_demo(req.symbol, req.timeframe, req.years, req.kind)


@router.get("/list")
def datasets():
    return {"datasets": list_datasets()}


@router.get("/summary")
def summary(dataset_id: str):
    meta = get_dataset(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df, _ = ingestion.load_dataset(dataset_id)
    preview = df.head(15).astype(str).to_dict(orient="records")
    return {"meta": meta, "report": meta.get("report", {}), "preview": preview}


@router.get("/features")
def features(dataset_id: str):
    df, meta = ingestion.load_dataset(dataset_id)
    if meta["kind"] == "tick":
        raise HTTPException(status_code=400, detail="Feature engineering needs OHLCV data.")
    _, report = build_features(df)
    return report
