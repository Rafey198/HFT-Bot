"""Tick replay engine — the runtime heart of the HFT terminal.

Runs a background thread that advances a tick stream and drives the full flow:
    onMarketTick -> scan signals -> spread guard -> risk manager
    -> execution queue -> paper broker -> position manager -> journal
The frontend polls state endpoints. WebSocket-ready (single shared state object).
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict, List, Optional

import pandas as pd

from ..core.config import symbol_spec
from ..core.logging import get_logger
from ..data import ingestion
from ..execution.execution_agent import ExecutionAgent
from ..execution.paper_broker import PaperBroker
from ..execution.position_manager import PositionManager
from ..journal.trade_journal import TradeJournal
from ..regimes.regime_detector import detect_regime
from ..risk.risk_manager import RiskManager
from .execution_queue import ExecutionQueue
from .latency_monitor import LatencyMonitor
from .market_feed import MarketFeed
from .signal_scanner import SignalScanner
from .spread_guard import SpreadGuard

log = get_logger("hft.replay")

TICKS_PER_DISPLAY_CANDLE = 8


class ReplayEngine:
    def __init__(self):
        self.lock = threading.RLock()
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.paused = False
        self.speed = 10
        self.symbol = "XAUUSD"
        self.timeframe = "M5"
        self.kind = "ohlcv"
        self.source = "simulated_tick"
        self.auto_execute = True
        self.cursor = 0
        self.total = 0
        self.clock = ""

        # Runtime components.
        self.risk = RiskManager()
        self.broker = PaperBroker(self.risk.balance)
        self.spread_guard = SpreadGuard(self.risk.settings["max_spread_points"])
        self.latency = LatencyMonitor()
        self.queue = ExecutionQueue(self.latency)
        self.scanner = SignalScanner()
        self.journal = TradeJournal(mode="paper")
        self.position_manager = PositionManager(self.broker, self.risk)
        self.agent = ExecutionAgent(self.spread_guard, self.risk, self.queue,
                                    self.broker, self.journal, self.position_manager)
        self.feed: Optional[MarketFeed] = None

        # Display state.
        self.last_tick: Dict = {}
        self.recent_signals: Deque[Dict] = deque(maxlen=60)
        self.recent_executions: Deque[Dict] = deque(maxlen=60)
        self.exec_log: Deque[Dict] = deque(maxlen=120)
        self.trade_markers: Deque[Dict] = deque(maxlen=200)
        self.display_candles: Deque[Dict] = deque(maxlen=200)
        self._cur_candle: Optional[Dict] = None
        self._candle_tick_count = 0
        self._vol_window: Deque[float] = deque(maxlen=80)
        self.recent_regime: Dict = {"regime": "ranging", "confidence": 0}
        self._df: Optional[pd.DataFrame] = None
        self._bind_close_journal()

    def _bind_close_journal(self):
        def on_close(pos: Dict):
            self.journal.log_close(pos, self.recent_regime.get("regime", ""))
            self.trade_markers.appendleft({
                "time": pos.get("exit_time"), "price": pos.get("exit_price"),
                "side": "close", "pnl": pos.get("pnl"),
            })
            self._log(f"CLOSE {pos['side']} {pos['symbol']} @ {pos['exit_price']} "
                      f"PnL {pos['pnl']:+.2f} ({pos.get('reason')})", "close")
        self.broker.on_close = on_close

    # --- lifecycle --------------------------------------------------------
    def start(self, dataset_id: Optional[str], symbol: str, timeframe: str,
              speed: int = 10, enabled_scalping: Optional[List[str]] = None,
              auto_execute: bool = True) -> Dict:
        with self.lock:
            self.stop()
            if dataset_id:
                df, meta = ingestion.load_dataset(dataset_id)
                symbol = meta["symbol"]
                timeframe = meta["timeframe"]
                kind = meta["kind"]
            else:
                df, meta = ingestion.get_or_create_default(symbol, timeframe, "ohlcv")
                kind = meta["kind"]

            self.symbol = symbol
            self.timeframe = timeframe
            self.kind = kind
            self.speed = max(1, int(speed))
            self.auto_execute = auto_execute
            self._df = df.tail(6000).reset_index(drop=True)

            self.feed = MarketFeed(self._df, symbol=symbol, kind=kind)
            self.source = self.feed.event_at(0)["source"] if self.feed.total else "simulated_tick"
            self.total = self.feed.total
            self.cursor = 0

            # Fresh runtime.
            self.risk.reset_account()
            self.risk.reset_kill_switch()
            self.broker.reset(self.risk.balance)
            self.scanner = SignalScanner(enabled=enabled_scalping or None)
            self.position_manager.reset()
            self.recent_signals.clear()
            self.recent_executions.clear()
            self.exec_log.clear()
            self.trade_markers.clear()
            self.display_candles.clear()
            self._cur_candle = None
            self._candle_tick_count = 0

            # Compute a regime snapshot from the source candles.
            try:
                self.recent_regime = detect_regime(self._df)
            except Exception:  # noqa: BLE001
                self.recent_regime = {"regime": "ranging", "confidence": 0}

            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            self._log(f"Replay started: {symbol} {timeframe} ({self.source}) "
                      f"@ {self.speed}x, auto_execute={auto_execute}", "system")
            return self.state()

    def pause(self) -> Dict:
        with self.lock:
            self.paused = True
            self._log("Replay paused.", "system")
            return self.state()

    def resume(self) -> Dict:
        with self.lock:
            if self.running:
                self.paused = False
                self._log("Replay resumed.", "system")
            return self.state()

    def set_speed(self, speed: int) -> Dict:
        with self.lock:
            self.speed = max(1, int(speed))
            return self.state()

    def reset(self) -> Dict:
        with self.lock:
            self.stop()
            self.cursor = 0
            self.risk.reset_account()
            self.risk.reset_kill_switch()
            self.broker.reset(self.risk.balance)
            self.recent_signals.clear()
            self.recent_executions.clear()
            self.exec_log.clear()
            self.trade_markers.clear()
            self.display_candles.clear()
            self._cur_candle = None
            self._log("Replay reset.", "system")
            return self.state()

    def stop(self) -> None:
        self.running = False
        t = self.thread
        if t and t.is_alive() and t is not threading.current_thread():
            t.join(timeout=1.0)
        self.thread = None

    # --- main loop --------------------------------------------------------
    def _loop(self) -> None:
        while self.running and self.cursor < self.total:
            if self.paused:
                time.sleep(0.1)
                continue
            batch = max(1, self.speed)
            for _ in range(batch):
                if self.cursor >= self.total:
                    break
                ev = self.feed.event_at(self.cursor)
                self.cursor += 1
                if ev:
                    self._on_tick(ev)
            time.sleep(0.1)
        self.running = False
        if self.cursor >= self.total:
            self._log("Replay finished — end of data.", "system")

    def _on_tick(self, tick: Dict) -> None:
        with self.lock:
            self.last_tick = tick
            self.clock = tick["timestamp"]
            self.latency.sample()
            self._update_display_candle(tick)

            # Position management every tick (SL/TP/trailing/timeout/kill).
            signals = self.scanner.scan(tick)
            self.position_manager.on_tick(tick, current_signals=signals)

            recent_vol = abs(self.scanner._micro_vol())
            if recent_vol > 0:
                self._vol_window.append(recent_vol)
            baseline_vol = (sorted(self._vol_window)[len(self._vol_window) // 2]
                            if self._vol_window else recent_vol)

            for sig in signals:
                sig["symbol"] = self.symbol
                self.recent_signals.appendleft(sig)
                self.journal.log_signal(sig, self.recent_regime.get("regime", ""))
                if sig["side"] == "hold":
                    continue
                if not self.auto_execute:
                    continue
                if self.risk.kill_switch_active:
                    sig["blocked_reason"] = "kill_switch"
                    continue
                result = self.agent.process_signal(
                    sig, tick, recent_vol=recent_vol,
                    atr=baseline_vol, regime=self.recent_regime.get("regime", ""),
                )
                if result["action"] == "open":
                    self.recent_executions.appendleft(result)
                    self.trade_markers.appendleft({
                        "time": tick["timestamp"], "price": result["entry"],
                        "side": result["side"], "type": "open",
                    })
                    self._log(f"OPEN {result['side'].upper()} {self.symbol} "
                              f"{result['lot_size']} lots @ {result['entry']} "
                              f"({sig['strategy']})", "open")
                elif result["action"] == "blocked":
                    sig["blocked_reason"] = result["reason"]
                    self._log(f"BLOCKED {sig['side'].upper()} {self.symbol} — {result['reason']}", "blocked")

    def _update_display_candle(self, tick: Dict) -> None:
        mid = float(tick["mid"])
        if self._cur_candle is None:
            self._cur_candle = {"time": tick["timestamp"], "open": mid,
                                "high": mid, "low": mid, "close": mid}
            self._candle_tick_count = 0
        c = self._cur_candle
        c["high"] = max(c["high"], mid)
        c["low"] = min(c["low"], mid)
        c["close"] = mid
        self._candle_tick_count += 1
        if self._candle_tick_count >= TICKS_PER_DISPLAY_CANDLE:
            self.display_candles.append(dict(c))
            self._cur_candle = None

    def _log(self, message: str, level: str = "info") -> None:
        self.exec_log.appendleft({"ts": self.clock or "", "level": level, "message": message})

    # --- accessors --------------------------------------------------------
    def kill_switch(self, activate: bool = True, reason: str = "Manual kill switch") -> Dict:
        with self.lock:
            if activate:
                self.risk.activate_kill_switch(reason)
                closed = self.broker.close_all(reason="kill_switch")
                for c in closed:
                    self.risk.on_trade_closed(c["pnl"])
                self._log(f"KILL SWITCH: {reason} — flattened {len(closed)} positions.", "kill")
            else:
                self.risk.reset_kill_switch()
                self._log("Kill switch reset.", "system")
            return self.risk.state()

    def state(self) -> Dict:
        return {
            "running": self.running,
            "paused": self.paused,
            "speed": self.speed,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "cursor": self.cursor,
            "total": self.total,
            "clock": self.clock,
            "auto_execute": self.auto_execute,
            "source": self.source,
            "progress": round(self.cursor / self.total * 100, 1) if self.total else 0,
        }

    def market_event(self) -> Dict:
        candles = list(self.display_candles)
        if self._cur_candle:
            candles = candles + [dict(self._cur_candle)]
        return {
            "tick": self.last_tick,
            "candles": candles[-160:],
            "markers": list(self.trade_markers)[:60],
            "regime": self.recent_regime,
            "state": self.state(),
        }

    def signals(self, limit: int = 40) -> List[Dict]:
        return list(self.recent_signals)[:limit]

    def execution_queue(self, limit: int = 40) -> List[Dict]:
        return self.queue.recent(limit)

    def logs(self, limit: int = 80) -> List[Dict]:
        return list(self.exec_log)[:limit]

    def scalping_stats(self) -> List[Dict]:
        from .signal_scanner import SCALPING_STRATEGIES
        # Group closed trades by strategy name.
        closed = self.broker.closed
        by_strategy: Dict[str, List[Dict]] = {}
        for t in closed:
            by_strategy.setdefault(t.get("strategy", ""), []).append(t)
        out = []
        for s in SCALPING_STRATEGIES:
            name = s["name"]
            trades = by_strategy.get(name, [])
            wins = [t for t in trades if t["pnl"] > 0]
            losses = [t for t in trades if t["pnl"] < 0]
            gross_w = sum(t["pnl"] for t in wins)
            gross_l = -sum(t["pnl"] for t in losses)
            pf = round(gross_w / gross_l, 2) if gross_l > 0 else (round(gross_w, 2) if gross_w else 0)
            out.append({
                "key": s["key"],
                "name": name,
                "enabled": s["key"] in self.scanner.enabled,
                "signal_count": self.scanner.stats.get(s["key"], {}).get("signals", 0),
                "trades": len(trades),
                "win_rate": round(len(wins) / len(trades) * 100, 1) if trades else 0,
                "profit_factor": pf,
                "avg_hold": 0,
                "max_drawdown": 0,
                "reject_reason": "" if s["key"] in self.scanner.enabled else "disabled",
            })
        return out


# Module-level singleton shared across all routes.
engine = ReplayEngine()
