"""Advanced animated theme: glassmorphism, motion graphics, animated background."""
from __future__ import annotations

import streamlit as st

DISCLAIMER = (
    "This system is for research, backtesting, and educational purposes. "
    "Forex and gold trading are high risk. Past performance does not guarantee "
    "future results. This system can lose money. Always use paper trading before "
    "live execution."
)

GOLD = "#f5c451"
BUY = "#16c784"
SELL = "#ea3943"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

:root { --gold:#f5c451; --buy:#16c784; --sell:#ea3943; --panel:#0f1524; --border:#1c2435; }

html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.stApp {
  background:
    radial-gradient(1200px 600px at 12% -10%, rgba(245,196,81,0.10), transparent 60%),
    radial-gradient(1000px 500px at 100% 0%, rgba(22,199,132,0.07), transparent 55%),
    linear-gradient(180deg, #05070d 0%, #070b16 100%);
  background-attachment: fixed;
}
/* animated grid overlay */
.stApp::before {
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.035) 1px, transparent 0);
  background-size: 26px 26px;
  animation: drift 24s linear infinite;
}
@keyframes drift { from{background-position:0 0;} to{background-position:26px 26px;} }

.mono { font-family:'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }

/* ---------- Hero ---------- */
.aurum-hero {
  position:relative; border-radius:20px; padding:38px 34px; overflow:hidden;
  background: linear-gradient(135deg, rgba(245,196,81,0.10), rgba(15,21,36,0.7) 45%, rgba(7,11,22,0.9));
  border:1px solid rgba(245,196,81,0.25);
  box-shadow: 0 0 50px rgba(245,196,81,0.10), inset 0 1px 0 rgba(255,255,255,0.04);
  animation: heroIn 0.9s cubic-bezier(.2,.8,.2,1) both;
}
@keyframes heroIn { from{opacity:0; transform:translateY(18px) scale(.99);} to{opacity:1; transform:none;} }
.aurum-hero h1 { font-size:2.5rem; font-weight:800; margin:0; letter-spacing:-1px;
  background:linear-gradient(90deg,#fff,#f5c451 60%,#b8902f);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.aurum-hero .sub { color:#9aa6bd; font-size:1.02rem; margin-top:8px; max-width:720px; line-height:1.55; }
.aurum-orb { position:absolute; border-radius:50%; filter:blur(40px); opacity:.5;
  animation: float 9s ease-in-out infinite; }
.orb1 { width:200px;height:200px; right:-40px; top:-50px; background:radial-gradient(circle,#f5c451,transparent 70%); }
.orb2 { width:160px;height:160px; right:160px; bottom:-60px; background:radial-gradient(circle,#16c784,transparent 70%); animation-delay:-3s;}
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-22px)} }

.badge { display:inline-flex; align-items:center; gap:7px; padding:5px 12px; border-radius:999px;
  border:1px solid rgba(245,196,81,0.4); color:#f5c451; font-size:.74rem; font-weight:600;
  background:rgba(245,196,81,0.08); text-transform:uppercase; letter-spacing:1px; }
.dot { width:8px;height:8px;border-radius:50%; background:#f5c451; box-shadow:0 0 10px #f5c451; animation:pulse 1.4s infinite; }
@keyframes pulse { 0%,100%{opacity:1; transform:scale(1)} 50%{opacity:.35; transform:scale(.7)} }

/* ---------- Metric cards ---------- */
.metric-grid { display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); }
.metric {
  position:relative; border-radius:14px; padding:16px 18px;
  background: linear-gradient(160deg, rgba(20,28,46,0.85), rgba(11,15,26,0.85));
  border:1px solid var(--border); overflow:hidden;
  box-shadow: 0 8px 26px rgba(0,0,0,0.40);
  animation: cardIn .6s ease both;
  transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
}
.metric:hover { transform:translateY(-4px); border-color:rgba(245,196,81,0.5); box-shadow:0 14px 34px rgba(245,196,81,0.12); }
.metric::after { content:""; position:absolute; left:0; top:0; height:3px; width:100%;
  background:linear-gradient(90deg,transparent,var(--gold),transparent); opacity:.7;
  animation: sweep 3.4s linear infinite; }
@keyframes sweep { from{transform:translateX(-100%)} to{transform:translateX(100%)} }
@keyframes cardIn { from{opacity:0; transform:translateY(14px)} to{opacity:1; transform:none} }
.metric .label { font-size:.66rem; text-transform:uppercase; letter-spacing:1.4px; color:#8b97ad; }
.metric .value { font-family:'JetBrains Mono',monospace; font-size:1.5rem; font-weight:700; margin-top:4px; }
.metric .value.buy{ color:var(--buy);} .metric .value.sell{ color:var(--sell);} .metric .value.gold{ color:var(--gold);}
.metric .sub { font-size:.72rem; color:#8b97ad; margin-top:2px; }

/* glass panel */
.glass { border-radius:16px; padding:18px 20px; border:1px solid var(--border);
  background:rgba(15,21,36,0.55); backdrop-filter:blur(8px); box-shadow:0 6px 24px rgba(0,0,0,0.4); }

/* live ticker */
.ticker { font-family:'JetBrains Mono',monospace; font-size:2.6rem; font-weight:700; letter-spacing:-1px; }
.flash-up { animation: fup .6s ease-out; color:var(--buy)!important; }
.flash-dn { animation: fdn .6s ease-out; color:var(--sell)!important; }
@keyframes fup { 0%{text-shadow:0 0 22px rgba(22,199,132,.9)} 100%{text-shadow:none} }
@keyframes fdn { 0%{text-shadow:0 0 22px rgba(234,57,67,.9)} 100%{text-shadow:none} }

.disclaimer { border-radius:12px; padding:12px 16px; font-size:.8rem; line-height:1.5;
  border:1px solid rgba(247,166,0,0.4); background:rgba(247,166,0,0.06); color:#f7a600; }

/* sidebar */
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0a0e18,#070b14); border-right:1px solid var(--border); }
.stButton>button { border-radius:10px; border:1px solid var(--border); font-weight:600; transition:all .2s; }
.stButton>button:hover { border-color:var(--gold); color:var(--gold); box-shadow:0 0 16px rgba(245,196,81,0.18); }
#MainMenu, footer { visibility:hidden; }

.pill { display:inline-block; padding:3px 10px; border-radius:999px; font-size:.7rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.5px; }
.pill.candidate{ color:var(--buy); border:1px solid rgba(22,199,132,.4); background:rgba(22,199,132,.1);}
.pill.paper_test{ color:#f7a600; border:1px solid rgba(247,166,0,.4); background:rgba(247,166,0,.1);}
.pill.reject{ color:var(--sell); border:1px solid rgba(234,57,67,.4); background:rgba(234,57,67,.1);}
</style>
"""


def inject_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, tag: str = "XAUUSD · Forex · 3D Quant Terminal") -> None:
    st.markdown(
        f"""
        <div class="aurum-hero">
          <div class="aurum-orb orb1"></div>
          <div class="aurum-orb orb2"></div>
          <span class="badge"><span class="dot"></span>{tag}</span>
          <h1>{title}</h1>
          <div class="sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_cards(cards: list[dict]) -> None:
    html = '<div class="metric-grid">'
    for i, c in enumerate(cards):
        tone = c.get("tone", "")
        sub = f'<div class="sub">{c["sub"]}</div>' if c.get("sub") else ""
        html += (
            f'<div class="metric" style="animation-delay:{i*0.05:.2f}s">'
            f'<div class="label">{c["label"]}</div>'
            f'<div class="value {tone}">{c["value"]}</div>{sub}</div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def disclaimer() -> None:
    st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)


def reco_pill(reco: str) -> str:
    return f'<span class="pill {reco}">{reco.replace("_", " ")}</span>'
