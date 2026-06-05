"use client";
import { useEffect, useState } from "react";
import { Play } from "lucide-react";
import { api } from "@/lib/api";
import { StrategyInfo } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button, Spinner } from "@/components/ui/primitives";
import { SymbolPicker } from "@/components/SymbolPicker";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { WarningBanner } from "@/components/dashboard/WarningBanner";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { cn, fmt, pctColor } from "@/lib/utils";

export default function WalkForwardPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("H1");
  const [strategyKey, setStrategyKey] = useState("ema_crossover");
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [res, setRes] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.strategies().then((d) => setStrategies(d.strategies)).catch(() => {}); }, []);

  const run = async () => {
    setLoading(true);
    try {
      const r = await api.walkForward({ strategy_key: strategyKey, symbol, timeframe, train_months: 24, test_months: 6 });
      setRes(r);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Walk-Forward Validation"
        subtitle="Rolling train/test windows on unseen out-of-sample data to reduce overfitting."
        right={
          <div className="flex flex-wrap items-center gap-2">
            <select value={strategyKey} onChange={(e) => setStrategyKey(e.target.value)} className="rounded-md border border-terminal-border bg-terminal-panel px-2 py-1.5 text-xs text-gray-200">
              {strategies.map((s) => <option key={s.key} value={s.key}>{s.name}</option>)}
            </select>
            <SymbolPicker symbol={symbol} timeframe={timeframe} onSymbol={setSymbol} onTimeframe={setTimeframe} />
            <Button variant="gold" onClick={run} disabled={loading}><Play size={14} /> Run</Button>
          </div>
        }
      />

      {loading && <div className="flex items-center gap-2 text-sm text-terminal-muted"><Spinner /> Validating…</div>}

      {res && (
        <>
          {res.overfitting_warning && <WarningBanner tone="danger">Overfitting warning — out-of-sample performance is unstable. {res.recommendation}</WarningBanner>}
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <MetricCard label="Avg OOS Return" value={<span className={pctColor(res.average_oos_return)}>{fmt(res.average_oos_return)}%</span>} />
            <MetricCard label="Avg OOS Drawdown" value={`${fmt(res.average_oos_drawdown)}%`} tone="sell" />
            <MetricCard label="Avg OOS PF" value={fmt(res.average_oos_profit_factor)} tone={res.average_oos_profit_factor >= 1.2 ? "buy" : "sell"} />
            <MetricCard label="Stability" value={`${res.stability_score}/100`} tone={res.stability_score >= 60 ? "buy" : "gold"} />
          </div>
          <Panel title={`Rolling Windows (${res.windows.length})`}>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[10px] uppercase text-terminal-muted">
                  <tr className="border-b border-terminal-border">
                    <th className="py-2 pr-3">Train</th><th className="pr-3">Test</th>
                    <th className="pr-3">OOS Return</th><th className="pr-3">OOS DD</th>
                    <th className="pr-3">OOS PF</th><th className="pr-3">Trades</th><th className="pr-3">Win%</th>
                  </tr>
                </thead>
                <tbody>
                  {res.windows.map((w: any, i: number) => (
                    <tr key={i} className="border-b border-terminal-border/40">
                      <td className="mono py-1.5 pr-3 text-terminal-muted">{w.train_start} → {w.train_end}</td>
                      <td className="mono pr-3 text-terminal-muted">{w.test_start} → {w.test_end}</td>
                      <td className={cn("mono pr-3", pctColor(w.oos_return))}>{fmt(w.oos_return)}%</td>
                      <td className="mono pr-3 text-warn">{fmt(w.oos_drawdown)}%</td>
                      <td className="mono pr-3">{fmt(w.oos_profit_factor)}</td>
                      <td className="mono pr-3">{w.oos_trades}</td>
                      <td className="mono pr-3">{fmt(w.oos_win_rate)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
          <div className="flex items-center gap-2 text-sm">
            <StatusBadge status={res.overfitting_warning ? "reject" : "candidate"} />
            <span className="text-terminal-muted">{res.recommendation}</span>
          </div>
        </>
      )}
    </div>
  );
}
