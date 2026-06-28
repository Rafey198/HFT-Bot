# AurumFX — HFT-Style Quant Execution Agent

> **HFT-style retail quant execution, backtesting, tick replay, paper trading, and risk-control terminal for XAUUSD/Forex.**

> ⚠️ **Disclaimer**
> This system is for research, backtesting, and educational purposes. Forex and gold trading are high risk. Past performance does not guarantee future results. **This system can lose money.** Always use paper trading before live execution.

**AurumFX is an HFT-style retail quant execution simulator. It mimics the workflow of fast execution systems using tick replay, rapid signal scanning, execution queues, latency monitoring, and strict risk controls. It is not institutional HFT and does not guarantee profit.**

---

## What this system is

AurumFX is a full-stack research and execution **simulator** for gold (XAUUSD) and major Forex pairs. It lets you:

- Load 10 years of historical OHLCV/tick data (or generate clearly-labelled synthetic demo data).
- Clean & validate data and produce a data-quality report.
- Engineer 37+ technical indicators, price-action, and session features.
- Run **35 modular trading strategies**.
- Run realistic backtests (spread, slippage, commission, risk sizing, no look-ahead).
- Run **walk-forward validation** to reduce overfitting.
- Detect **market regime** and select strategies based on regime + robustness.
- Replay ticks at 1x–100x and watch an **HFT-style terminal** scan signals, queue orders, and paper-fill them under strict risk control.
- Track everything in a trade journal and export reports.

## Why it is HFT-*style*, not true HFT

True institutional HFT relies on co-located servers, microsecond/nanosecond latency, direct market access, and order-book microstructure. AurumFX runs on retail data and a normal web stack. It **reproduces the workflow and ergonomics** of fast execution systems — tick replay, rapid signal scanning, an execution queue with simulated latency/slippage, latency meters, spread guards, and a risk kill switch — but it is a research simulator. **It does not provide a real low-latency trading edge and does not guarantee profit.**

---

## Features

- **Fast market feed** — tick + simulated-tick streaming, live price ticker, bid/ask, spread meter, latency meter.
- **Signal scanner** — 10 fast scalping strategies scan every tick; signals expire quickly and never fire without a stop loss.
- **Execution queue** — full order lifecycle (received → risk_checking → approved → queued → executing → filled/rejected/expired) with latency & slippage simulation and duplicate/stale guards.
- **Strict risk management** — hard caps (per-trade, daily, weekly, drawdown, trade-rate, consecutive losses, open positions, min R:R, min confidence, max spread), automatic + manual **kill switch**. The risk manager overrides all signals.
- **35 strategies** across trend, momentum, volatility, session, price-action, ensemble, and ML categories.
- **Realistic backtester** + **walk-forward validation** + **regime detection** + **strategy selection**.
- **Paper broker** with balance/equity tracking, SL/TP/trailing, position manager.
- **Optional MT5 adapter** (safe placeholder when MetaTrader5 is not installed; live trading locked by default).
- **Trade journal, reports, explainability & safety agents.**
- **Professional dark hedge-fund terminal UI** with gold XAUUSD accents, animated feeds, and live charts.

## Architecture

```
Data Ingestion → Feature Engineering → 35 Strategies → Backtest → Walk-Forward → Regime
                                                                         │
 Tick Replay → Market Feed → Signal Scanner → Spread Guard → Risk Manager → Execution Queue
                                                                         │
                                              Paper Broker / MT5 → Position Manager → Journal
```

- **Backend:** Python + FastAPI + Pandas/NumPy/Scikit-learn + SQLite.
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS + Recharts + Framer Motion + Lucide icons.

```
backend/app/   core · schemas · data · features · strategies · backtesting
               regimes · selection · risk · hft · execution · agents · journal · reports · api
frontend/      app/<pages> · components/<layout|hft|charts|trading|dashboard|ui> · lib
```

---

## 🟡 Streamlit edition (3D + motion-graphics UI)

A self-contained **Streamlit** app provides an immersive **3D + motion-graphics** interface that
**reuses the same Python engine** in `backend/app` — no API server required. It ships demo data and
lets you **upload your own CSV to test the model**.

```bash
pip install -r requirements.txt        # root requirements (Streamlit deployment)
streamlit run streamlit_app.py         # http://localhost:8501
```

Deploy to **Streamlit Community Cloud**: push to GitHub → share.streamlit.io → New app → Main file
path = `streamlit_app.py` (root `requirements.txt` and `.streamlit/config.toml` are auto-detected).

Highlights:
- Animated gradient/grid background, glassmorphism metric cards, motion transitions.
- **3D charts**: equity ribbon, price-path build-up, monthly-returns surface, strategy landscape, regime space.
- **Animated HFT terminal** with live signal scanner, execution queue, paper fills, risk gauges, kill switch.
- **Data Center → Upload your data** (tick or OHLCV CSV) to run strategies/backtests/replay on it.
- Ready-made sample files in `sample_data/` (`XAUUSD_M5_sample.csv`, `XAUUSD_ticks_sample.csv`, `EURUSD_M15_sample.csv`).

---

## Backend setup (FastAPI API + Next.js terminal)

Requirements: Python 3.10+

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API docs: http://127.0.0.1:8000/docs · Health: http://127.0.0.1:8000/health

`pandas-ta` and `MetaTrader5` are **optional**. Indicators are implemented manually, so `pandas-ta` is not required. The MT5 adapter degrades to a safe placeholder when `MetaTrader5` is unavailable.

## Frontend setup

Requirements: Node 18+

```bash
cd frontend
npm install
# Point the UI at your backend (defaults to http://127.0.0.1:8000):
echo "NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000" > .env.local
npm run dev      # http://localhost:3000
# production:
npm run build && npm start
```

---

## How to run demo mode

Demo mode works with **no uploaded data and no broker**.

1. Start the backend and frontend.
2. Open the app and click **“Run Demo Replay”** on the Home page (or open **HFT Terminal**).
3. Watch prices update, signals appear, paper orders queue and fill, positions open and close on SL/TP, and the journal update.
4. Hit the **kill switch** to flatten positions and halt execution.

The backend auto-generates synthetic XAUUSD-like OHLCV data and a simulated tick stream, clearly labelled as simulated.

## How to upload real CSV

Go to **Data Center → Upload CSV**. Two formats are supported:

- **Tick:** `timestamp,bid,ask,volume`
- **OHLCV:** `timestamp,open,high,low,close,volume`

The ingestion agent validates columns, parses/sorts timestamps, removes duplicates and invalid rows, detects missing candles, infers timeframe, and returns a data-quality report.

## How to run a backtest

Open **Backtest**, pick a strategy, symbol, and timeframe, set risk %, and click **Run Backtest**. You get equity curve, drawdown, monthly-returns heatmap, full metrics (CAGR, Sharpe, Sortino, Calmar, profit factor, expectancy, max drawdown, etc.), a trade table, and a `reject / paper_test / candidate` recommendation. Use **Strategy Lab → Run All** for the leaderboard, and **Walk-Forward** to test out-of-sample robustness.

## How to run tick replay

Open **Tick Replay**, choose speed (1x/5x/10x/50x/100x), and Start/Pause/Reset. Upload a tick or OHLCV CSV to replay your own data, toggle paper execution, and export replay trades to CSV.

## How to paper trade

Open **Paper Trading** and click **Start Paper Session** (or use the HFT Terminal). The paper broker tracks balance/equity, opens/closes trades on SL/TP, and records everything to the journal. No real money is involved.

## How live trading is locked

Live trading is **disabled by default**. The **Live Execution** page stays locked until **all** of these pass:

1. Live Mode toggle enabled
2. Confirmation phrase typed exactly: **`I understand this can lose money`**
3. Broker adapter connected & symbol verified
4. Risk settings valid
5. Safety Agent passes
6. Paper trading record exists
7. Kill switch visible
8. Max daily loss not reached

Even when all checks pass, this demo will **not** place real orders unless a real MetaTrader 5 terminal is installed and the order is explicitly approved by the risk manager.

## How the kill switch works

The kill switch is always visible in the HFT Terminal and Risk Kill Center. It can be triggered:

- **Manually** — flattens all open positions and blocks new orders until reset.
- **Automatically** — when max daily loss or max drawdown caps are breached.

The risk manager overrides all signals: no trade is sent without a stop loss, acceptable spread, sufficient confidence, valid reward:risk, and available risk budget.

## Risk rules (defaults)

```json
{
  "initial_balance": 10000,
  "risk_per_trade": 0.25,
  "max_daily_loss": 2.0,
  "max_weekly_loss": 5.0,
  "max_drawdown_stop": 10.0,
  "max_trades_per_minute": 5,
  "max_trades_per_day": 50,
  "max_consecutive_losses": 3,
  "max_open_positions": 2,
  "min_reward_risk": 1.2,
  "max_spread_points": 30,
  "min_signal_confidence": 60
}
```

Editable in **Settings**. No martingale, grid, or averaging-down logic is used anywhere.

## Limitations

- Synthetic data is a regime-switching random walk — useful for workflow demos, **not** a model of real markets.
- Backtest/paper PnL uses simplified contract sizing and quote-currency assumptions.
- Latency and slippage are **simulated**, not measured against a real broker.
- The ML strategy is a simple logistic-regression demo (train-on-first-half), not a production model.
- This is **not** institutional HFT and provides no real low-latency edge.

## Future improvements

- WebSocket streaming (the architecture is WebSocket-ready; polling is used today).
- Real broker/data integrations and tick-accurate microstructure modelling.
- Parameter optimization & Bayesian search in walk-forward.
- Portfolio-level risk and correlation controls.
- Persistent multi-session paper accounts and richer reporting/PDF export.
