"use client";
import { useEffect, useState } from "react";
import { Play } from "lucide-react";
import { api } from "@/lib/api";
import { BacktestResult, StrategyInfo } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button, Spinner } from "@/components/ui/primitives";
import { SymbolPicker } from "@/components/SymbolPicker";
import { BacktestMetrics } from "@/components/trading/BacktestMetrics";
import { EquityCurve, DrawdownChart } from "@/components/charts/EquityCurve";
import { MonthlyReturnsHeatmap } from "@/components/charts/MonthlyReturnsHeatmap";
import { ClosedTradesPanel } from "@/components/hft/ClosedTradesPanel";
import { WarningBanner } from "@/components/dashboard/WarningBanner";

export default function BacktestPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("M5");
  const [strategyKey, setStrategyKey] = useState("donchian_breakout");
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [risk, setRisk] = useState(0.25);
  const [trailing, setTrailing] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => { api.strategies().then((d) => setStrategies(d.strategies)).catch(() => {}); }, []);

  const run = async () => {
    setLoading(true); setErr("");
    try {
      const r: any = await api.backtest({
        strategy_key: strategyKey, symbol, timeframe,
        risk_per_trade: risk, use_trailing_stop: trailing,
      });
      setResult(r);
    } catch (e) { setErr((e as Error).message); } finally { setLoading(false); }
  };

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Backtest"
        subtitle="Realistic backtester with spread, slippage, commission, and risk sizing."
        right={
          <div className="flex flex-wrap items-center gap-2">
            <select value={strategyKey} onChange={(e) => setStrategyKey(e.target.value)} className="rounded-md border border-terminal-border bg-terminal-panel px-2 py-1.5 text-xs text-gray-200">
              {strategies.map((s) => <option key={s.key} value={s.key}>{s.name}</option>)}
            </select>
            <SymbolPicker symbol={symbol} timeframe={timeframe} onSymbol={setSymbol} onTimeframe={setTimeframe} />
            <Button variant="gold" onClick={run} disabled={loading}><Play size={14} /> Run Backtest</Button>
          </div>
        }
      />

      <Panel title="Parameters">
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <label className="flex items-center gap-2">
            <span className="text-terminal-muted">Risk per trade %</span>
            <input type="number" step="0.05" value={risk} onChange={(e) => setRisk(parseFloat(e.target.value))} className="mono w-20 rounded border border-terminal-border bg-terminal-panel px-2 py-1" />
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={trailing} onChange={(e) => setTrailing(e.target.checked)} />
            <span className="text-terminal-muted">Trailing stop</span>
          </label>
        </div>
      </Panel>

      {loading && <div className="flex items-center gap-2 text-sm text-terminal-muted"><Spinner /> Backtesting…</div>}
      {err && <WarningBanner tone="danger">{err}</WarningBanner>}

      {result && (
        <>
          <BacktestMetrics r={result} />
          {result.warnings?.map((w, i) => <WarningBanner key={i}>{w}</WarningBanner>)}
          {result.safety?.warnings?.map((w, i) => <WarningBanner key={`s${i}`}>{w}</WarningBanner>)}

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Panel title="Equity Curve"><EquityCurve data={result.equity_curve} /></Panel>
            <Panel title="Drawdown"><DrawdownChart data={result.drawdown_curve} /></Panel>
          </div>
          <Panel title="Monthly Returns (%)"><MonthlyReturnsHeatmap data={result.monthly_returns} /></Panel>
          <Panel title={`Trades (${result.trades.length})`}><ClosedTradesPanel trades={result.trades} /></Panel>
        </>
      )}
    </div>
  );
}
