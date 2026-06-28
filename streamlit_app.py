"""
AurumFX — HFT-Style Quant Execution Agent (Streamlit edition)
Advanced 3D + motion-graphics UI. Reuses the FastAPI backend engine (backend/app).

Research/education only. Not institutional HFT. Live trading is disabled.
Run:  streamlit run streamlit_app.py
"""
from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from streamlit_lib import engine, theme, viz

st.set_page_config(
    page_title="AurumFX — 3D HFT Quant Terminal",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded",
)
theme.inject_theme()

ss = st.session_state
ss.setdefault("frame", 0)
ss.setdefault("df", None)
ss.setdefault("fdf", None)
ss.setdefault("report", None)
ss.setdefault("data_label", None)
ss.setdefault("data_symbol", "XAUUSD")
ss.setdefault("data_kind", "ohlcv")
ss.setdefault("results", [])
ss.setdefault("replay", None)
ss.setdefault("replay_running", False)
ss.setdefault("replay_speed", 8)


def k() -> str:
    ss.frame += 1
    return f"k{ss.frame}"


# --------------------------------------------------------------------------- data
@st.cache_data(show_spinner=False)
def demo_dataset(symbol: str, timeframe: str, years: float):
    df = engine.generate_demo_df(symbol, timeframe, years)
    fdf, frep = engine.features(df)
    rep = {
        "symbol": symbol, "timeframe": timeframe, "rows": len(df),
        "start_date": str(df["timestamp"].iloc[0]), "end_date": str(df["timestamp"].iloc[-1]),
        "missing_candles": 0, "duplicate_rows_removed": 0, "invalid_rows_removed": 0,
        "data_quality_score": 100.0, "kind": "ohlcv",
        "warnings": ["SIMULATED OHLCV data — not real market data."],
    }
    return df, fdf, rep


def ensure_dataset():
    if ss.df is None:
        with st.spinner("Generating simulated XAUUSD demo data + features…"):
            df, fdf, rep = demo_dataset("XAUUSD", "M5", 5.0)
            _set_dataset(df, fdf, rep, "Demo · XAUUSD M5 (simulated)", "XAUUSD", "ohlcv")


def _set_dataset(df, fdf, rep, label, symbol, kind):
    ss.df, ss.fdf, ss.report = df, fdf, rep
    ss.data_label, ss.data_symbol, ss.data_kind = label, symbol, kind
    ss.results = []


# --------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;padding:6px 2px 14px">'
        '<div style="width:38px;height:38px;border-radius:10px;background:rgba(245,196,81,.15);'
        'display:flex;align-items:center;justify-content:center;color:#f5c451;font-weight:800;'
        'box-shadow:0 0 18px rgba(245,196,81,.3)">Au</div>'
        '<div><div style="color:#f5c451;font-weight:800;font-size:1.05rem">AurumFX</div>'
        '<div style="color:#8b97ad;font-size:.62rem;letter-spacing:2px">3D HFT QUANT</div></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigate",
        ["🏠 Overview", "🗄️ Data Center", "🧪 Strategy Lab", "📊 Backtest",
         "🔁 Walk-Forward", "🛰️ Regime Monitor", "⚡ HFT Terminal", "🛡️ Risk & Kill Switch",
         "🚀 Deploy / About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if ss.data_label:
        st.caption(f"Active dataset:\n\n**{ss.data_label}**")
    else:
        st.caption("No dataset loaded yet.")
    st.markdown(
        '<div style="margin-top:10px;font-size:.62rem;color:#6b7689;line-height:1.5">'
        'Live trading disabled by default. Research & paper only.</div>',
        unsafe_allow_html=True,
    )


def metric_row(cards):
    theme.metric_cards(cards)


def logs_html(logs, height=240):
    colors = {"open": "#16c784", "close": "#f5c451", "blocked": "#f7a600",
              "kill": "#ff2d55", "system": "#8b97ad", "info": "#cdd5e3"}
    rows = ""
    for l in logs:
        c = colors.get(l["level"], "#cdd5e3")
        ts = str(l.get("ts", ""))[11:19]
        rows += (f'<div style="display:flex;gap:8px"><span style="color:#566">{ts}</span>'
                 f'<span style="color:{c};text-transform:uppercase">[{l["level"]}]</span>'
                 f'<span style="color:#cdd5e3">{l["message"]}</span></div>')
    if not rows:
        rows = '<div style="color:#566">Execution log empty…</div>'
    return (f'<div class="glass mono" style="height:{height}px;overflow:auto;font-size:.72rem;'
            f'line-height:1.6">{rows}</div>')


# =========================================================================== OVERVIEW
if page == "🏠 Overview":
    theme.hero(
        "AurumFX — 3D HFT-Style Quant Terminal",
        "HFT-style retail quant execution, backtesting, tick replay, paper trading and "
        "risk-control — now with an immersive 3D + motion-graphics interface on Streamlit. "
        "It mimics fast execution workflows (tick replay, rapid signal scanning, execution "
        "queues, latency monitoring, strict risk control). It is <b>not</b> institutional HFT "
        "and does <b>not</b> guarantee profit.",
    )
    st.write("")
    theme.disclaimer()
    st.write("")

    ensure_dataset()
    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(viz.price_path_3d(
            [{"open": r.open, "high": r.high, "low": r.low, "close": r.close}
             for r in ss.df.tail(120).itertuples()]),
            use_container_width=True, key=k())
    with c2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### What you can do")
        for t in ["Generate or **upload your own** CSV (tick / OHLCV) to test the model",
                  "Run **35 strategies** + realistic backtests with 3D analytics",
                  "Walk-forward validation to fight overfitting",
                  "3D market-regime space + regime-aware selection",
                  "Animated **HFT terminal** with live signals, execution queue & kill switch"]:
            st.markdown(f"- {t}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Pipeline")
    steps = ["Data", "Features", "35 Strategies", "Backtest", "Walk-Forward",
             "Regime", "Signal Scanner", "Spread Guard", "Risk Manager",
             "Execution Queue", "Paper Broker", "Journal"]
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:8px">' +
        "".join(f'<span class="badge" style="border-color:#1c2435;color:#cdd5e3;'
                f'background:rgba(15,21,36,.6)">{s}</span>' for s in steps) +
        "</div>", unsafe_allow_html=True)

# =========================================================================== DATA CENTER
elif page == "🗄️ Data Center":
    theme.hero("Data Center", "Generate simulated demo data or upload your own CSV to test the model.",
               tag="Tick & OHLCV ingestion")
    st.write("")
    tab_demo, tab_upload = st.tabs(["✨ Demo data", "📤 Upload your data"])

    with tab_demo:
        c1, c2, c3 = st.columns(3)
        symbol = c1.selectbox("Symbol", engine.SYMBOLS, index=0)
        timeframe = c2.selectbox("Timeframe", engine.TIMEFRAMES, index=1)
        years = c3.slider("History (years)", 1.0, 10.0, 5.0, 1.0)
        if st.button("⚡ Generate demo dataset", type="primary"):
            with st.spinner("Generating simulated data + 37 features…"):
                df, fdf, rep = demo_dataset(symbol, timeframe, years)
                _set_dataset(df, fdf, rep, f"Demo · {symbol} {timeframe} (simulated)", symbol, "ohlcv")
            st.success(f"Generated {len(df):,} rows of simulated {symbol} {timeframe} data.")

    with tab_upload:
        st.markdown("Upload a CSV in one of these formats:")
        st.code("timestamp,bid,ask,volume\ntimestamp,open,high,low,close,volume", language="text")
        cup1, cup2 = st.columns([2, 1])
        up_symbol = cup1.selectbox("Symbol label", engine.SYMBOLS, index=0, key="up_sym")
        up_tf = cup2.selectbox("Timeframe (OHLCV)", engine.TIMEFRAMES, index=1, key="up_tf")
        file = st.file_uploader("Your CSV (tick or OHLCV)", type=["csv"])
        if file is not None and st.button("📥 Ingest & test with my data", type="primary"):
            try:
                with st.spinner("Validating, cleaning & engineering features on your data…"):
                    df, rep, kind = engine.parse_uploaded_csv(file.getvalue(), up_symbol, up_tf)
                    fdf, _ = engine.features(df)
                    rep["symbol"] = up_symbol
                    _set_dataset(df, fdf, rep, f"Your data · {up_symbol} ({kind})", up_symbol, kind)
                st.success(f"Ingested {len(df):,} usable rows from your file. "
                           f"Now use Strategy Lab / Backtest / HFT Terminal to test the model.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not parse your CSV: {exc}")

        st.markdown("###### Don't have data? Download a ready-made sample to try the upload flow:")
        cols = st.columns(3)
        for col, path, lbl in zip(
            cols,
            ["sample_data/XAUUSD_M5_sample.csv", "sample_data/XAUUSD_ticks_sample.csv",
             "sample_data/EURUSD_M15_sample.csv"],
            ["XAUUSD M5 (OHLCV)", "XAUUSD ticks", "EURUSD M15 (OHLCV)"]):
            try:
                with open(path, "rb") as fh:
                    col.download_button(f"⬇ {lbl}", fh.read(), file_name=path.split("/")[-1],
                                        mime="text/csv", use_container_width=True)
            except OSError:
                pass

    if ss.report:
        st.write("")
        r = ss.report
        metric_row([
            {"label": "Rows", "value": f"{r['rows']:,}"},
            {"label": "Quality", "value": r["data_quality_score"],
             "tone": "buy" if r["data_quality_score"] > 80 else "gold"},
            {"label": "Kind", "value": r["kind"]},
            {"label": "Missing", "value": r["missing_candles"]},
            {"label": "Duplicates", "value": r["duplicate_rows_removed"]},
            {"label": "Invalid", "value": r["invalid_rows_removed"]},
        ])
        for w in r.get("warnings", []):
            st.warning(w)
        st.markdown("###### Preview")
        st.dataframe(ss.df.head(12), use_container_width=True, height=240)

# =========================================================================== STRATEGY LAB
elif page == "🧪 Strategy Lab":
    theme.hero("Strategy Lab", "35 modular strategies across trend, momentum, volatility, session, "
               "price-action, ensemble and ML — compared on a 3D landscape.", tag="35 strategies")
    ensure_dataset()
    st.write("")
    info = engine.strategies_info()
    cats = engine.categories()
    st.caption(f"{len(info)} strategies · " + " · ".join(f"{c}:{len(v)}" for c, v in cats.items()))

    if st.button("🚀 Run all 35 strategies on active dataset", type="primary"):
        with st.spinner("Backtesting 35 strategies…"):
            ss.results = engine.backtest_all(ss.fdf, ss.data_symbol, ss.report["timeframe"])

    if ss.results:
        good = [r for r in ss.results if not r.get("error")]
        st.plotly_chart(viz.leaderboard_3d(good), use_container_width=True, key=k())
        st.markdown("###### Leaderboard")
        tbl = pd.DataFrame([{
            "Strategy": r["strategy_name"], "Return %": r.get("total_return", 0),
            "PF": r.get("profit_factor", 0), "Max DD %": r.get("max_drawdown", 0),
            "Sharpe": r.get("sharpe", 0), "Trades": r.get("num_trades", 0),
            "Verdict": r.get("recommendation", "reject"),
        } for r in good])
        st.dataframe(tbl, use_container_width=True, height=420)
    else:
        st.markdown('<div class="glass">Run the suite to populate the 3D strategy landscape.</div>',
                    unsafe_allow_html=True)

    with st.expander("Browse strategy descriptions"):
        for cat, keys in cats.items():
            st.markdown(f"**{cat.title()}**")
            for s in [x for x in info if x["category"] == cat]:
                st.markdown(f"- `{s['key']}` — {s['name']}: {s['description']}")

# =========================================================================== BACKTEST
elif page == "📊 Backtest":
    theme.hero("Backtest", "Realistic engine (spread, slippage, commission, risk sizing, no look-ahead) "
               "with 3D equity ribbon and a monthly-returns surface.", tag="3D analytics")
    ensure_dataset()
    st.write("")
    keys = engine.strategy_keys()
    info = {s["key"]: s["name"] for s in engine.strategies_info()}
    c1, c2, c3 = st.columns([2, 1, 1])
    key = c1.selectbox("Strategy", keys, index=keys.index("donchian_breakout") if "donchian_breakout" in keys else 0,
                       format_func=lambda x: info.get(x, x))
    risk = c2.number_input("Risk per trade %", 0.05, 2.0, 0.25, 0.05)
    trailing = c3.checkbox("Trailing stop", value=False)

    if st.button("📈 Run backtest", type="primary"):
        with st.spinner("Backtesting on active dataset…"):
            ss["bt"] = engine.backtest_one(ss.fdf, key, ss.data_symbol, ss.report["timeframe"], risk, trailing)

    r = ss.get("bt")
    if r:
        metric_row([
            {"label": "Total Return", "value": f"{r['total_return']}%",
             "tone": "buy" if r["total_return"] >= 0 else "sell"},
            {"label": "CAGR", "value": f"{r['cagr']}%"},
            {"label": "Win Rate", "value": f"{r['win_rate']}%"},
            {"label": "Profit Factor", "value": r["profit_factor"],
             "tone": "buy" if r["profit_factor"] >= 1.2 else "sell"},
            {"label": "Max Drawdown", "value": f"{r['max_drawdown']}%", "tone": "sell"},
            {"label": "Sharpe", "value": r["sharpe"]},
            {"label": "Sortino", "value": r["sortino"]},
            {"label": "Trades", "value": r["num_trades"]},
        ])
        st.markdown(f'Recommendation: {theme.reco_pill(r["recommendation"])}', unsafe_allow_html=True)
        for w in r.get("warnings", []):
            st.warning(w)

        st.plotly_chart(viz.equity_ribbon_3d(r["equity_curve"], r["drawdown_curve"]),
                        use_container_width=True, key=k())
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.equity_area(r["equity_curve"]), use_container_width=True, key=k())
        c2.plotly_chart(viz.drawdown_area(r["drawdown_curve"]), use_container_width=True, key=k())
        st.plotly_chart(viz.monthly_surface_3d(r["monthly_returns"]), use_container_width=True, key=k())
        if r.get("trades"):
            st.markdown("###### Trades")
            st.dataframe(pd.DataFrame(r["trades"]), use_container_width=True, height=300)
    else:
        st.markdown('<div class="glass">Pick a strategy and run a backtest to see 3D analytics.</div>',
                    unsafe_allow_html=True)

# =========================================================================== WALK-FORWARD
elif page == "🔁 Walk-Forward":
    theme.hero("Walk-Forward Validation", "Rolling train/test windows on unseen out-of-sample data to "
               "reduce overfitting.", tag="Out-of-sample")
    ensure_dataset()
    st.write("")
    keys = engine.strategy_keys()
    info = {s["key"]: s["name"] for s in engine.strategies_info()}
    c1, c2, c3 = st.columns([2, 1, 1])
    key = c1.selectbox("Strategy", keys, index=keys.index("ema_crossover") if "ema_crossover" in keys else 0,
                       format_func=lambda x: info.get(x, x))
    train = c2.slider("Train (months)", 6, 36, 24, 3)
    test = c3.slider("Test (months)", 1, 12, 6, 1)
    if st.button("🔬 Run walk-forward", type="primary"):
        with st.spinner("Running rolling out-of-sample validation…"):
            ss["wf"] = engine.walk_forward(ss.fdf, key, ss.data_symbol, ss.report["timeframe"], train, test)

    wf = ss.get("wf")
    if wf:
        if wf["overfitting_warning"]:
            st.error(f"⚠️ Overfitting warning — {wf['recommendation']}")
        else:
            st.success(wf["recommendation"])
        metric_row([
            {"label": "Avg OOS Return", "value": f"{wf['average_oos_return']}%",
             "tone": "buy" if wf["average_oos_return"] >= 0 else "sell"},
            {"label": "Avg OOS DD", "value": f"{wf['average_oos_drawdown']}%", "tone": "sell"},
            {"label": "Avg OOS PF", "value": wf["average_oos_profit_factor"],
             "tone": "buy" if wf["average_oos_profit_factor"] >= 1.2 else "sell"},
            {"label": "Stability", "value": f"{wf['stability_score']}/100",
             "tone": "buy" if wf["stability_score"] >= 60 else "gold"},
        ])
        if wf["windows"]:
            st.dataframe(pd.DataFrame(wf["windows"]), use_container_width=True, height=320)
    else:
        st.markdown('<div class="glass">Run validation to see rolling out-of-sample windows.</div>',
                    unsafe_allow_html=True)

# =========================================================================== REGIME
elif page == "🛰️ Regime Monitor":
    theme.hero("Regime Monitor", "Market-regime detection visualised in a 3D state space "
               "(ADX × volatility × momentum).", tag="Regime aware")
    ensure_dataset()
    st.write("")
    reg = engine.detect_regime(ss.fdf)
    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(viz.regime_scatter_3d(ss.fdf), use_container_width=True, key=k())
    with c2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(f"### `{reg['regime'].replace('_', ' ')}`")
        st.caption(f"Confidence {reg['confidence']}%")
        st.write(reg["reason"])
        st.markdown("**Recommended:** " + (", ".join(reg["recommended_strategy_types"]) or "stand aside"))
        st.markdown("**Avoid:** " + (", ".join(reg["avoid_strategy_types"]) or "—"))
        st.markdown("</div>", unsafe_allow_html=True)
        if not ss.results:
            st.info("Run 'Strategy Lab → Run all' to enable regime-aware selection ranking.")

# =========================================================================== HFT TERMINAL
elif page == "⚡ HFT Terminal":
    theme.hero("HFT Terminal — Live Demo Replay", "Animated tick replay with live signal scanning, "
               "execution queue, paper fills and an always-on kill switch. No broker or data required.",
               tag="Live motion")
    ensure_dataset()
    st.write("")

    c1, c2, c3, c4, c5 = st.columns([1.4, 1.4, 1, 1.4, 1.4])
    if c1.button("▶ Start / Restart demo", type="primary", use_container_width=True):
        ss.replay = engine.ReplaySession(ss.df, ss.data_symbol, ss.data_kind)
        ss.replay_running = True
        st.rerun()
    if c2.button(("⏸ Pause" if ss.replay_running else "▶ Resume"), use_container_width=True):
        if ss.replay is not None:
            ss.replay_running = not ss.replay_running
        st.rerun()
    ss.replay_speed = c3.select_slider("Speed", [1, 5, 8, 20, 50, 100], value=ss.replay_speed,
                                       label_visibility="collapsed")
    if c4.button("⛔ KILL SWITCH", use_container_width=True):
        if ss.replay:
            ss.replay.kill(True)
        st.rerun()
    if c5.button("♻ Reset risk / re-arm", use_container_width=True):
        if ss.replay:
            ss.replay.kill(False)
        st.rerun()

    ph_status = st.empty()
    top = st.columns([1.1, 2, 1.2])
    ph_feed = top[0].empty()
    ph_chart = top[1].empty()
    ph_signals = top[2].empty()
    mid = st.columns([2, 1.2])
    ph_queue = mid[0].empty()
    ph_risk = mid[1].empty()
    ph_logs = st.empty()

    def render(snap):
        t = snap["tick"]
        risk = snap["risk"]
        lat = snap["latency"]
        digits = 2 if (t.get("mid", 0) or 0) > 50 else 5
        with ph_status.container():
            theme.metric_cards([
                {"label": "Symbol", "value": t.get("symbol", ss.data_symbol), "tone": "gold"},
                {"label": "Mid", "value": f"{t.get('mid', 0):.{digits}f}"},
                {"label": "Spread", "value": f"{t.get('spread', 0):.{digits}f}"},
                {"label": "Latency", "value": f"{lat.get('total_latency_ms', 0):.0f}ms",
                 "sub": lat.get("status", "")},
                {"label": "Equity", "value": f"${risk.get('equity', 0):,.0f}",
                 "tone": "buy" if risk.get("daily_pnl", 0) >= 0 else "sell"},
                {"label": "Day P/L", "value": f"{risk.get('daily_pnl_percent', 0)}%",
                 "tone": "buy" if risk.get("daily_pnl", 0) >= 0 else "sell"},
                {"label": "Progress", "value": f"{snap['progress']}%"},
            ])
        with ph_feed.container():
            cls = "ticker"
            st.markdown(f'<div class="glass"><div class="label" style="color:#8b97ad;'
                        f'font-size:.65rem;letter-spacing:1px">LIVE PRICE</div>'
                        f'<div class="{cls}" style="color:#f5c451">{t.get("mid", 0):.{digits}f}</div>'
                        f'<div class="mono" style="color:#8b97ad;font-size:.8rem">'
                        f'bid {t.get("bid", 0):.{digits}f} · ask {t.get("ask", 0):.{digits}f}</div>'
                        f'<div class="mono" style="margin-top:6px;color:#8b97ad;font-size:.72rem">'
                        f'regime: {snap["regime"].get("regime", "—")}<br>source: {snap["source"]}</div>'
                        f'</div>', unsafe_allow_html=True)
        with ph_chart.container():
            st.plotly_chart(viz.live_candles(snap["candles"], snap["markers"]),
                            use_container_width=True, key=k())
        with ph_signals.container():
            html = '<div class="glass" style="height:380px;overflow:auto"><div class="label" '\
                   'style="color:#8b97ad;font-size:.65rem;letter-spacing:1px;margin-bottom:6px">'\
                   'SIGNAL SCANNER</div>'
            for s in snap["signals"][:14]:
                col = "#16c784" if s["side"] == "buy" else ("#ea3943" if s["side"] == "sell" else "#8b97ad")
                blk = f'<div style="color:#f7a600;font-size:.62rem">blk: {s["blocked_reason"]}</div>' if s.get("blocked_reason") else ""
                html += (f'<div style="border:1px solid #1c2435;border-radius:8px;padding:5px 8px;'
                         f'margin-bottom:5px;background:rgba(15,21,36,.5)">'
                         f'<div style="display:flex;justify-content:space-between">'
                         f'<span style="color:#cdd5e3;font-size:.74rem">{s["strategy"]}</span>'
                         f'<span class="mono" style="color:{col};font-weight:700">{s["side"].upper()}</span></div>'
                         f'<div class="mono" style="color:#8b97ad;font-size:.62rem">@{s["entry"]:.2f} · conf {s["confidence"]}</div>{blk}</div>')
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        with ph_queue.container():
            st.markdown('<div class="label" style="color:#8b97ad;font-size:.65rem;letter-spacing:1px">EXECUTION QUEUE</div>', unsafe_allow_html=True)
            if snap["orders"]:
                st.dataframe(pd.DataFrame(snap["orders"])[
                    ["order_id", "side", "state", "requested_price", "filled_price", "latency_ms", "slippage", "reason"]
                ].head(8), use_container_width=True, height=220, hide_index=True)
            else:
                st.caption("No orders yet…")
        with ph_risk.container():
            st.plotly_chart(viz.risk_gauge(min(0, risk.get("daily_pnl_percent", 0)),
                            risk.get("max_daily_loss", 2), "Daily loss used"),
                            use_container_width=True, key=k())
            ks = risk.get("kill_switch_active")
            st.markdown(f'<div style="text-align:center;font-weight:700;color:{"#ff2d55" if ks else "#16c784"}">'
                        f'{"⛔ KILLED — " + risk.get("kill_reason", "") if ks else "● ARMED · execution live"}</div>',
                        unsafe_allow_html=True)
        with ph_logs.container():
            bs = snap["broker"]
            st.markdown(f'<div style="color:#8b97ad;font-size:.72rem;margin-bottom:4px">'
                        f'Open {bs["open_count"]} · Closed {bs["closed_count"]} · '
                        f'Balance ${bs["balance"]:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(logs_html(snap["logs"], 200), unsafe_allow_html=True)

    if ss.replay is None:
        st.markdown('<div class="glass">Press <b>Start / Restart demo</b> to launch the animated terminal. '
                    'It auto-generates a tick stream from the active dataset — no broker or upload needed.</div>',
                    unsafe_allow_html=True)
    else:
        sess = ss.replay
        if ss.replay_running and sess.cursor < sess.total:
            for _ in range(10):
                if sess.cursor >= sess.total:
                    break
                sess.step(ss.replay_speed)
                render(sess.snapshot())
                time.sleep(0.12)
            if sess.cursor >= sess.total:
                ss.replay_running = False
            else:
                st.rerun()
        else:
            render(sess.snapshot())
            if sess.cursor >= sess.total and sess.total:
                st.info("Replay finished — press Start / Restart to run again.")

# =========================================================================== RISK
elif page == "🛡️ Risk & Kill Switch":
    theme.hero("Risk & Kill Switch", "The risk manager overrides all signals: hard caps, auto/manual "
               "kill switch, and live limit usage.", tag="Risk first")
    st.write("")
    if ss.replay is None:
        st.markdown('<div class="glass">Start a session in the <b>HFT Terminal</b> to populate live risk state, '
                    'or review the default caps below.</div>', unsafe_allow_html=True)
        rm = engine.RiskManager()
        risk = rm.state()
        settings = rm.settings
    else:
        risk = ss.replay.risk.state()
        settings = ss.replay.risk.settings

    metric_row([
        {"label": "Balance", "value": f"${risk['balance']:,.0f}"},
        {"label": "Equity", "value": f"${risk['equity']:,.0f}", "tone": "gold"},
        {"label": "Day P/L", "value": f"{risk['daily_pnl_percent']}%",
         "tone": "buy" if risk["daily_pnl"] >= 0 else "sell"},
        {"label": "Drawdown", "value": f"{risk['drawdown_percent']}%", "tone": "sell"},
        {"label": "Open", "value": risk["open_positions"]},
        {"label": "Trades today", "value": risk["trades_today"]},
        {"label": "Loss streak", "value": risk["consecutive_losses"]},
        {"label": "Kill switch", "value": "ON" if risk["kill_switch_active"] else "off",
         "tone": "sell" if risk["kill_switch_active"] else "buy"},
    ])
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(viz.risk_gauge(min(0, risk["daily_pnl_percent"]), settings["max_daily_loss"],
                    "Daily loss cap"), use_container_width=True, key=k())
    c2.plotly_chart(viz.risk_gauge(risk["drawdown_percent"], settings["max_drawdown_stop"],
                    "Drawdown cap"), use_container_width=True, key=k())
    c3.plotly_chart(viz.risk_gauge(risk["trades_per_minute"], settings["max_trades_per_minute"],
                    "Trades / min cap"), use_container_width=True, key=k())

    with st.expander("Risk rule defaults"):
        st.json(settings)

# =========================================================================== DEPLOY
elif page == "🚀 Deploy / About":
    theme.hero("Deploy on Streamlit", "One-file entrypoint, root requirements, themed config — ready for "
               "Streamlit Community Cloud.", tag="Deployment")
    st.write("")
    theme.disclaimer()
    st.markdown("""
#### Deploy to Streamlit Community Cloud
1. Push this repo to GitHub.
2. Go to **share.streamlit.io → New app**.
3. Pick the repo/branch and set **Main file path** = `streamlit_app.py`.
4. Deploy. Root `requirements.txt` and `.streamlit/config.toml` are picked up automatically.

#### Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

#### Notes
- The Streamlit app **reuses the FastAPI backend engine** in `backend/app` (no API server needed).
- This is a research simulator — **not institutional HFT**, no guaranteed profit, live trading disabled.
""")
    st.markdown("**3D + motion-graphics features:** animated gradient/grid background, glassmorphism metric "
                "cards with sweep animation, 3D equity ribbon, 3D price-path build-up, 3D monthly-returns "
                "surface, 3D strategy landscape, 3D regime space, animated live HFT terminal, and risk gauges.")
