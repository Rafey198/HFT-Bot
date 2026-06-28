"""Adapters that reuse the FastAPI backend engine (backend/app) inside Streamlit."""
from __future__ import annotations

import io
import os
import sys
from collections import deque
from typing import Deque, Dict, List, Optional, Tuple

import pandas as pd

# --- make the backend package importable -----------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND = os.path.join(_REPO, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from app.backtesting.engine import BacktestConfig, run_backtest  # noqa: E402
from app.backtesting.walk_forward import run_walk_forward  # noqa: E402
from app.data import synthetic_data, validation  # noqa: E402
from app.execution.execution_agent import ExecutionAgent  # noqa: E402
from app.execution.paper_broker import PaperBroker  # noqa: E402
from app.execution.position_manager import PositionManager  # noqa: E402
from app.features.pipeline import build_features  # noqa: E402
from app.hft.execution_queue import ExecutionQueue  # noqa: E402
from app.hft.latency_monitor import LatencyMonitor  # noqa: E402
from app.hft.market_feed import MarketFeed  # noqa: E402
from app.hft.signal_scanner import SCALPING_STRATEGIES, SignalScanner  # noqa: E402
from app.hft.spread_guard import SpreadGuard  # noqa: E402
from app.regimes.regime_detector import detect_regime as _detect_regime  # noqa: E402
from app.risk.risk_manager import RiskManager  # noqa: E402
from app.strategies.registry import (REGISTRY, all_keys, category_map,  # noqa: E402
                                     get_strategy, list_strategy_info)

SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]


# --- data ------------------------------------------------------------------
def generate_demo_df(symbol: str = "XAUUSD", timeframe: str = "M5", years: float = 10.0) -> pd.DataFrame:
    df = synthetic_data.generate_ohlcv(symbol, timeframe, years)
    df, _ = validation.validate_ohlcv(df, timeframe)
    return df


def parse_uploaded_csv(content: bytes, symbol: str, timeframe: str) -> Tuple[pd.DataFrame, Dict, str]:
    """Returns (clean_df, quality_report, kind)."""
    raw = pd.read_csv(io.BytesIO(content))
    raw.columns = [c.strip().lower() for c in raw.columns]
    kind = validation.detect_kind(raw)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], utc=True, errors="coerce")
    if kind == "tick":
        df, rep = validation.validate_tick(raw)
        tf = "tick"
        from app.data.preprocessing import ticks_to_ohlcv
        ohlcv = ticks_to_ohlcv(df, "M1")
        ohlcv, _ = validation.validate_ohlcv(ohlcv, "M1")
        report = _report(df, "M1", rep, "tick")
        return ohlcv, report, "tick"
    tf = timeframe or validation.infer_timeframe(raw)
    df, rep = validation.validate_ohlcv(raw, tf)
    return df, _report(df, tf, rep, "ohlcv"), "ohlcv"


def _report(df: pd.DataFrame, tf: str, rep: Dict, kind: str) -> Dict:
    score = validation.quality_score(rep, len(df))
    return {
        "symbol": "", "timeframe": tf, "rows": len(df),
        "start_date": str(df["timestamp"].iloc[0]) if len(df) else "",
        "end_date": str(df["timestamp"].iloc[-1]) if len(df) else "",
        "missing_candles": rep.get("missing_candles", 0),
        "duplicate_rows_removed": rep.get("duplicate_rows_removed", 0),
        "invalid_rows_removed": rep.get("invalid_rows_removed", 0),
        "data_quality_score": score, "kind": kind,
        "warnings": rep.get("warnings", []),
    }


def features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    return build_features(df)


# --- research --------------------------------------------------------------
def strategies_info() -> List[Dict]:
    return list_strategy_info()


def strategy_keys() -> List[str]:
    return all_keys()


def categories() -> Dict[str, List[str]]:
    return category_map()


def backtest_one(fdf: pd.DataFrame, key: str, symbol: str, timeframe: str,
                 risk_per_trade: float = 0.25, trailing: bool = False,
                 params: Optional[Dict] = None) -> Dict:
    cfg = BacktestConfig(symbol=symbol, timeframe=timeframe,
                         risk_per_trade=risk_per_trade, use_trailing_stop=trailing)
    strat = get_strategy(key, params)
    res = run_backtest(fdf, strat, cfg)
    res["strategy_key"] = key
    return res


def backtest_all(fdf: pd.DataFrame, symbol: str, timeframe: str,
                 risk_per_trade: float = 0.25, max_bars: int = 60000) -> List[Dict]:
    cfg = BacktestConfig(symbol=symbol, timeframe=timeframe, risk_per_trade=risk_per_trade)
    df = fdf.tail(max_bars).reset_index(drop=True) if len(fdf) > max_bars else fdf
    out = []
    for key in all_keys():
        try:
            res = run_backtest(df, get_strategy(key), cfg, with_curves=False, max_trades_keep=0)
            res["strategy_key"] = key
            res.pop("trades", None)
            out.append(res)
        except Exception as exc:  # noqa: BLE001
            out.append({"strategy_key": key, "strategy_name": key, "error": str(exc),
                        "num_trades": 0, "recommendation": "reject"})
    out.sort(key=lambda r: (r.get("profit_factor", 0), r.get("total_return", 0)), reverse=True)
    return out


def walk_forward(fdf: pd.DataFrame, key: str, symbol: str, timeframe: str,
                 train_months: int = 24, test_months: int = 6) -> Dict:
    cfg = BacktestConfig(symbol=symbol, timeframe=timeframe)
    return run_walk_forward(fdf, key, cfg, train_months, test_months)


def detect_regime(fdf: pd.DataFrame) -> Dict:
    return _detect_regime(fdf)


# --- live HFT replay session (synchronous, Streamlit-friendly) -------------
TICKS_PER_DISPLAY_CANDLE = 8


class ReplaySession:
    """Drives the full HFT flow step-by-step for animated Streamlit rendering."""

    def __init__(self, df: pd.DataFrame, symbol: str, kind: str = "ohlcv",
                 risk_settings: Optional[Dict] = None, enabled_scalping: Optional[List[str]] = None,
                 auto_execute: bool = True):
        self.symbol = symbol
        self.auto_execute = auto_execute
        self.feed = MarketFeed(df.reset_index(drop=True), symbol=symbol, kind=kind)
        self.total = self.feed.total
        self.cursor = 0
        self.source = self.feed.event_at(0)["source"] if self.total else "simulated_tick"

        self.risk = RiskManager(risk_settings)
        self.risk.reset_account()
        self.broker = PaperBroker(self.risk.balance)
        self.spread_guard = SpreadGuard(self.risk.settings["max_spread_points"])
        self.latency = LatencyMonitor()
        self.queue = ExecutionQueue(self.latency)
        self.scanner = SignalScanner(enabled=enabled_scalping or None)
        self.position_manager = PositionManager(self.broker, self.risk)
        self.agent = ExecutionAgent(self.spread_guard, self.risk, self.queue,
                                    self.broker, journal=None, position_manager=self.position_manager)

        self.last_tick: Dict = {}
        self.signals: Deque[Dict] = deque(maxlen=40)
        self.logs: Deque[Dict] = deque(maxlen=80)
        self.markers: Deque[Dict] = deque(maxlen=120)
        self.display_candles: Deque[Dict] = deque(maxlen=160)
        self._cur: Optional[Dict] = None
        self._ct = 0
        self._vol: Deque[float] = deque(maxlen=80)
        try:
            self.regime = detect_regime(df) if kind == "ohlcv" else {"regime": "n/a", "confidence": 0}
        except Exception:  # noqa: BLE001
            self.regime = {"regime": "ranging", "confidence": 0}
        self.broker.on_close = self._on_close

    def _on_close(self, pos: Dict):
        self.markers.appendleft({"time": pos.get("exit_time"), "price": pos.get("exit_price"),
                                 "side": "close", "pnl": pos.get("pnl")})
        self._log(f"CLOSE {pos['side'].upper()} @ {pos['exit_price']} PnL {pos['pnl']:+.2f} ({pos.get('reason')})", "close")

    def _log(self, msg: str, level: str = "info"):
        self.logs.appendleft({"ts": self.last_tick.get("timestamp", ""), "level": level, "message": msg})

    def _candle(self, tick: Dict):
        mid = float(tick["mid"])
        if self._cur is None:
            self._cur = {"time": tick["timestamp"], "open": mid, "high": mid, "low": mid, "close": mid}
            self._ct = 0
        c = self._cur
        c["high"] = max(c["high"], mid); c["low"] = min(c["low"], mid); c["close"] = mid
        self._ct += 1
        if self._ct >= TICKS_PER_DISPLAY_CANDLE:
            self.display_candles.append(dict(c)); self._cur = None

    def step(self, n: int = 1) -> None:
        for _ in range(n):
            if self.cursor >= self.total:
                return
            tick = self.feed.event_at(self.cursor)
            self.cursor += 1
            if not tick:
                continue
            tick["symbol"] = self.symbol
            self.last_tick = tick
            self.latency.sample()
            self._candle(tick)
            sigs = self.scanner.scan(tick)
            self.position_manager.on_tick(tick, current_signals=sigs)
            rv = abs(self.scanner._micro_vol())
            if rv > 0:
                self._vol.append(rv)
            base = sorted(self._vol)[len(self._vol) // 2] if self._vol else rv
            for s in sigs:
                s["symbol"] = self.symbol
                self.signals.appendleft(s)
                if s["side"] == "hold" or not self.auto_execute or self.risk.kill_switch_active:
                    continue
                res = self.agent.process_signal(s, tick, recent_vol=rv, atr=base,
                                                regime=self.regime.get("regime", ""))
                if res["action"] == "open":
                    self.markers.appendleft({"time": tick["timestamp"], "price": res["entry"],
                                             "side": res["side"], "type": "open"})
                    self._log(f"OPEN {res['side'].upper()} {res['lot_size']} lots @ {res['entry']} ({s['strategy']})", "open")
                elif res["action"] == "blocked":
                    s["blocked_reason"] = res["reason"]
                    self._log(f"BLOCKED {s['side'].upper()} — {res['reason']}", "blocked")

    def kill(self, activate: bool = True):
        if activate:
            self.risk.activate_kill_switch("Manual kill switch (Streamlit)")
            for c in self.broker.close_all("kill_switch"):
                self.risk.on_trade_closed(c["pnl"])
            self._log("KILL SWITCH — positions flattened, execution halted.", "kill")
        else:
            self.risk.reset_kill_switch()
            self._log("Kill switch reset.", "system")

    def snapshot(self) -> Dict:
        candles = list(self.display_candles)
        if self._cur:
            candles = candles + [dict(self._cur)]
        bs = self.broker.state()
        return {
            "tick": self.last_tick,
            "candles": candles,
            "markers": list(self.markers),
            "signals": list(self.signals),
            "orders": self.queue.recent(20),
            "logs": list(self.logs),
            "risk": self.risk.state(),
            "latency": self.latency.current(),
            "broker": bs,
            "regime": self.regime,
            "progress": round(self.cursor / self.total * 100, 1) if self.total else 0,
            "cursor": self.cursor, "total": self.total, "source": self.source,
            "done": self.cursor >= self.total,
        }
