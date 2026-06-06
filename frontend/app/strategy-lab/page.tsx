"use client";
import { useEffect, useState } from "react";
import { Play, Layers } from "lucide-react";
import { api } from "@/lib/api";
import { StrategyInfo, BacktestResult } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button, Spinner } from "@/components/ui/primitives";
import { SymbolPicker } from "@/components/SymbolPicker";
import { StrategyLeaderboard } from "@/components/trading/StrategyLeaderboard";
import { cn } from "@/lib/utils";

const CAT_LABELS: Record<string, string> = {
  trend: "Trend", momentum: "Momentum", volatility: "Volatility",
  session: "Session", price_action: "Price Action", ensemble: "Ensemble", ml: "ML",
};

export default function StrategyLabPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("M5");
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<BacktestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [singleRun, setSingleRun] = useState<any>(null);

  useEffect(() => {
    api.strategies().then((d) => {
      setStrategies(d.strategies);
      setEnabled(Object.fromEntries(d.strategies.map((s: StrategyInfo) => [s.key, true])));
    }).catch(() => {});
  }, []);

  const runOne = async (key: string) => {
    setLoading(true);
    try {
      const r = await api.runStrategy({ strategy_key: key, symbol, timeframe });
      setSingleRun(r);
    } catch (e) { setSingleRun({ error: (e as Error).message }); } finally { setLoading(false); }
  };

  const runAll = async () => {
    setLoading(true);
    try {
      const r: any = await api.backtestAll({ symbol, timeframe, top_n: 35 });
      setResults(r.results);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  const byCat = strategies.reduce<Record<string, StrategyInfo[]>>((acc, s) => {
    (acc[s.category] = acc[s.category] || []).push(s);
    return acc;
  }, {});

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Strategy Lab"
        subtitle={`${strategies.length} modular strategies. Enable, inspect, and compare.`}
        right={
          <div className="flex items-center gap-2">
            <SymbolPicker symbol={symbol} timeframe={timeframe} onSymbol={setSymbol} onTimeframe={setTimeframe} />
            <Button variant="gold" onClick={runAll} disabled={loading}><Layers size={14} /> Run All</Button>
          </div>
        }
      />

      {loading && <div className="flex items-center gap-2 text-sm text-terminal-muted"><Spinner /> Running…</div>}

      {results.length > 0 && (
        <Panel title="Comparison Leaderboard">
          <StrategyLeaderboard results={results} onSelect={runOne} />
        </Panel>
      )}

      {singleRun && !singleRun.error && (
        <Panel title={`Latest Signal — ${singleRun.strategy?.name}`}>
          <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            <Info label="Buy signals" value={singleRun.buy_signals} />
            <Info label="Sell signals" value={singleRun.sell_signals} />
            <Info label="Latest side" value={singleRun.latest_signal?.signal} />
            <Info label="Confidence" value={singleRun.latest_signal?.confidence} />
          </div>
          <p className="mt-2 text-xs text-terminal-muted">{singleRun.latest_signal?.reason}</p>
        </Panel>
      )}

      <div className="space-y-4">
        {Object.entries(byCat).map(([cat, list]) => (
          <Panel key={cat} title={CAT_LABELS[cat] || cat}>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
              {list.map((s) => (
                <div key={s.key} className={cn("rounded-md border p-3", enabled[s.key] ? "border-terminal-border bg-terminal-card" : "border-terminal-border bg-terminal-panel/40 opacity-60")}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-gray-100">{s.name}</span>
                    <button
                      onClick={() => setEnabled((p) => ({ ...p, [s.key]: !p[s.key] }))}
                      className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase", enabled[s.key] ? "border border-buy/40 text-buy" : "border border-terminal-border text-terminal-muted")}
                    >
                      {enabled[s.key] ? "On" : "Off"}
                    </button>
                  </div>
                  <p className="mt-1 text-xs leading-relaxed text-terminal-muted">{s.description}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="mono text-[10px] text-terminal-muted">{Object.keys(s.parameters).length} params</span>
                    <Button size="sm" onClick={() => runOne(s.key)}><Play size={12} /> Run</Button>
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: any }) {
  return (
    <div className="rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2">
      <div className="text-[10px] uppercase text-terminal-muted">{label}</div>
      <div className="mono text-base font-semibold text-gray-100">{String(value ?? "—")}</div>
    </div>
  );
}
