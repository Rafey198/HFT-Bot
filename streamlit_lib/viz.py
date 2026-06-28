"""Plotly 3D + motion-graphics visualizations for the AurumFX Streamlit app."""
from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
import plotly.graph_objects as go

GOLD = "#f5c451"
BUY = "#16c784"
SELL = "#ea3943"
GRID = "#1c2435"
PAPER = "rgba(0,0,0,0)"


def _layout(fig: go.Figure, height: int = 420, title: str = "") -> go.Figure:
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(color="#e6eaf2", size=15)),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(color="#9aa6bd", family="JetBrains Mono"),
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        legend=dict(bgcolor="rgba(15,21,36,0.6)", bordercolor=GRID, borderwidth=1),
    )
    return fig


def _scene(fig: go.Figure, xaxis="X", yaxis="Y", zaxis="Z") -> go.Figure:
    axis = dict(backgroundcolor=PAPER, gridcolor=GRID, zerolinecolor=GRID,
                showbackground=True, color="#7c8aa5")
    fig.update_layout(scene=dict(
        xaxis=dict(title=xaxis, **axis),
        yaxis=dict(title=yaxis, **axis),
        zaxis=dict(title=zaxis, **axis),
        bgcolor=PAPER,
        camera=dict(eye=dict(x=1.6, y=1.5, z=0.9)),
    ))
    return fig


def equity_ribbon_3d(equity_curve: List[dict], drawdown_curve: List[dict] | None = None,
                     height: int = 460) -> go.Figure:
    """A glowing 3D equity ribbon: x=time index, y=drawdown, z=equity."""
    if not equity_curve:
        return _layout(go.Figure(), height, "Equity (3D)")
    eq = pd.DataFrame(equity_curve)
    x = np.arange(len(eq))
    z = eq["equity"].to_numpy()
    if drawdown_curve:
        dd = pd.DataFrame(drawdown_curve)["drawdown"].to_numpy()
        if len(dd) != len(z):
            dd = np.interp(np.linspace(0, 1, len(z)), np.linspace(0, 1, len(dd)), dd)
    else:
        roll = np.maximum.accumulate(z)
        dd = (z - roll) / np.where(roll == 0, 1, roll) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x, y=dd, z=z, mode="lines",
        line=dict(width=7, color=z, colorscale=[[0, SELL], [0.5, GOLD], [1, BUY]]),
        name="Equity path",
    ))
    fig.add_trace(go.Scatter3d(
        x=x, y=dd, z=np.full_like(z, z.min()), mode="lines",
        line=dict(width=2, color="rgba(245,196,81,0.25)"), name="Shadow", showlegend=False,
    ))
    _scene(fig, "Time →", "Drawdown %", "Equity $")
    return _layout(fig, height, "Equity Ribbon — 3D (time × drawdown × equity)")


def price_path_3d(candles: List[dict], height: int = 460, animate: bool = True) -> go.Figure:
    """Animated 3D price path: x=index, y=intrabar range, z=mid price."""
    if not candles:
        return _layout(go.Figure(), height, "Price Path (3D)")
    df = pd.DataFrame(candles)
    x = np.arange(len(df))
    z = df["close"].to_numpy()
    y = (df["high"] - df["low"]).to_numpy()
    up = df["close"].to_numpy() >= df["open"].to_numpy()
    colors = np.where(up, BUY, SELL)

    base = go.Scatter3d(
        x=x, y=y, z=z, mode="lines+markers",
        line=dict(width=5, color=z, colorscale=[[0, "#3a2b00"], [0.5, GOLD], [1, "#fff3cf"]]),
        marker=dict(size=2.5, color=colors), name="Price",
    )
    fig = go.Figure(data=[base])

    if animate and len(df) > 12:
        steps = np.linspace(8, len(df), 18, dtype=int)
        frames = [go.Frame(data=[go.Scatter3d(
            x=x[:k], y=y[:k], z=z[:k], mode="lines+markers",
            line=dict(width=5, color=z[:k], colorscale=[[0, "#3a2b00"], [0.5, GOLD], [1, "#fff3cf"]]),
            marker=dict(size=2.5, color=colors[:k]))]) for k in steps]
        fig.frames = frames
        fig.update_layout(updatemenus=[dict(
            type="buttons", showactive=False, x=0.02, y=0.02, xanchor="left",
            bgcolor="rgba(15,21,36,0.8)", bordercolor=GRID,
            buttons=[dict(label="▶ Play build-up", method="animate",
                          args=[None, dict(frame=dict(duration=70, redraw=True), fromcurrent=True)])],
        )])
    _scene(fig, "Tick →", "Bar range", "Price")
    return _layout(fig, height, "Price Path — 3D motion build-up")


def monthly_surface_3d(monthly_returns: List[dict], height: int = 460) -> go.Figure:
    """3D surface of monthly returns by year × month."""
    if not monthly_returns:
        return _layout(go.Figure(), height, "Monthly Returns (3D)")
    rows = {}
    for m in monthly_returns:
        y, mm = m["month"].split("-")
        rows.setdefault(y, {})[int(mm)] = m["return"]
    years = sorted(rows)
    z = [[rows[y].get(mo, 0.0) for mo in range(1, 13)] for y in years]
    fig = go.Figure(data=[go.Surface(
        z=z, x=list(range(1, 13)), y=years,
        colorscale=[[0, SELL], [0.5, "#0f1524"], [1, BUY]], cmid=0,
        contours=dict(z=dict(show=True, color=GRID, width=1)),
        colorbar=dict(title="%", tickfont=dict(color="#9aa6bd")),
    )])
    _scene(fig, "Month", "Year", "Return %")
    return _layout(fig, height, "Monthly Returns — 3D surface")


def leaderboard_3d(results: List[dict], height: int = 480) -> go.Figure:
    """3D scatter of strategies: x=max drawdown, y=profit factor, z=total return."""
    rows = [r for r in results if r.get("num_trades", 0) > 0]
    if not rows:
        return _layout(go.Figure(), height, "Strategy Landscape (3D)")
    df = pd.DataFrame(rows)
    size = (df["num_trades"].clip(1) ** 0.4)
    size = (size / size.max() * 26 + 6)
    fig = go.Figure(data=[go.Scatter3d(
        x=df["max_drawdown"], y=df["profit_factor"], z=df["total_return"],
        mode="markers+text",
        text=df["strategy_name"], textposition="top center",
        textfont=dict(size=8, color="#7c8aa5"),
        marker=dict(size=size, color=df["profit_factor"],
                    colorscale=[[0, SELL], [0.45, GOLD], [1, BUY]], cmin=0.6, cmax=1.8,
                    line=dict(width=0.5, color="#05070d"), opacity=0.92,
                    colorbar=dict(title="PF", tickfont=dict(color="#9aa6bd"))),
        hovertemplate="<b>%{text}</b><br>DD %{x:.1f}%<br>PF %{y:.2f}<br>Return %{z:.1f}%<extra></extra>",
    )])
    _scene(fig, "Max Drawdown %", "Profit Factor", "Total Return %")
    return _layout(fig, height, "Strategy Landscape — 3D (DD × PF × Return, size = trades)")


def regime_scatter_3d(df: pd.DataFrame, height: int = 460) -> go.Figure:
    """3D scatter of recent bars: ADX × ATR-percentile × momentum, colored by direction."""
    if df is None or df.empty or "adx" not in df.columns:
        return _layout(go.Figure(), height, "Regime Space (3D)")
    d = df.dropna(subset=["adx", "atr"]).tail(1500).copy()
    atr_pct = d["atr"].rank(pct=True) * 100
    mom = (d["close"].pct_change(10).fillna(0) * 100)
    fig = go.Figure(data=[go.Scatter3d(
        x=d["adx"], y=atr_pct, z=mom, mode="markers",
        marker=dict(size=3, color=mom, colorscale=[[0, SELL], [0.5, GOLD], [1, BUY]],
                    cmid=0, opacity=0.7),
        hovertemplate="ADX %{x:.0f}<br>ATR pct %{y:.0f}<br>Mom %{z:.2f}%<extra></extra>",
    )])
    _scene(fig, "ADX (trend)", "ATR percentile (vol)", "10-bar momentum %")
    return _layout(fig, height, "Market Regime Space — 3D")


def equity_area(equity_curve: List[dict], height: int = 280) -> go.Figure:
    fig = go.Figure()
    if equity_curve:
        eq = pd.DataFrame(equity_curve)
        fig.add_trace(go.Scatter(
            x=list(range(len(eq))), y=eq["equity"], mode="lines",
            line=dict(color=GOLD, width=2), fill="tozeroy",
            fillcolor="rgba(245,196,81,0.12)", name="Equity"))
    fig.update_xaxes(showgrid=False, color="#7c8aa5")
    fig.update_yaxes(gridcolor=GRID, color="#7c8aa5")
    return _layout(fig, height, "")


def drawdown_area(dd_curve: List[dict], height: int = 220) -> go.Figure:
    fig = go.Figure()
    if dd_curve:
        dd = pd.DataFrame(dd_curve)
        fig.add_trace(go.Scatter(
            x=list(range(len(dd))), y=dd["drawdown"], mode="lines",
            line=dict(color=SELL, width=1.5), fill="tozeroy",
            fillcolor="rgba(234,57,67,0.18)", name="Drawdown"))
    fig.update_xaxes(showgrid=False, color="#7c8aa5")
    fig.update_yaxes(gridcolor=GRID, color="#7c8aa5")
    return _layout(fig, height, "")


def live_candles(candles: List[dict], markers: List[dict] | None = None, height: int = 380) -> go.Figure:
    fig = go.Figure()
    if candles:
        df = pd.DataFrame(candles)
        fig.add_trace(go.Candlestick(
            x=list(range(len(df))), open=df["open"], high=df["high"], low=df["low"], close=df["close"],
            increasing=dict(line=dict(color=BUY), fillcolor=BUY),
            decreasing=dict(line=dict(color=SELL), fillcolor=SELL), name="XAUUSD"))
        if candles:
            last = df["close"].iloc[-1]
            fig.add_hline(y=last, line=dict(color=GOLD, width=1, dash="dot"))
    fig.update_xaxes(showgrid=False, rangeslider=dict(visible=False), color="#7c8aa5")
    fig.update_yaxes(gridcolor=GRID, color="#7c8aa5", side="right")
    return _layout(fig, height, "")


def risk_gauge(value: float, max_value: float, title: str, height: int = 220) -> go.Figure:
    pct = min(100, abs(value) / max_value * 100) if max_value else 0
    color = BUY if pct < 50 else (GOLD if pct < 80 else SELL)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct,
        number=dict(suffix="%", font=dict(color=color, size=26)),
        title=dict(text=title, font=dict(color="#9aa6bd", size=12)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#7c8aa5"),
            bar=dict(color=color),
            bgcolor=PAPER, borderwidth=1, bordercolor=GRID,
            steps=[dict(range=[0, 50], color="rgba(22,199,132,0.12)"),
                   dict(range=[50, 80], color="rgba(245,196,81,0.12)"),
                   dict(range=[80, 100], color="rgba(234,57,67,0.15)")],
            threshold=dict(line=dict(color=SELL, width=3), value=100)),
    ))
    return _layout(fig, height, "")
