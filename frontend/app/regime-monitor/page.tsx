"use client";
import { useState } from "react";
import { Radar, Search } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button, Spinner, Badge } from "@/components/ui/primitives";
import { SymbolPicker } from "@/components/SymbolPicker";
import { MetricCard } from "@/components/dashboard/MetricCard";

const REGIME_COLORS: Record<string, string> = {
  trending_bullish: "text-buy", trending_bearish: "text-sell",
  ranging: "text-gold", high_volatility: "text-warn",
  low_volatility: "text-terminal-muted", news_like_spike: "text-danger", choppy_avoid: "text-danger",
};

export default function RegimeMonitorPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("M5");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const detect = async () => {
    setLoading(true);
    try { setData(await api.regime({ symbol, timeframe })); } catch { /* ignore */ } finally { setLoading(false); }
  };

  const regime = data?.regime;
  const selection = data?.selection;

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Regime Monitor"
        subtitle="Detect market regime and align strategy selection accordingly."
        right={
          <div className="flex items-center gap-2">
            <SymbolPicker symbol={symbol} timeframe={timeframe} onSymbol={setSymbol} onTimeframe={setTimeframe} />
            <Button variant="gold" onClick={detect} disabled={loading}><Search size={14} /> Detect</Button>
          </div>
        }
      />

      {loading && <div className="flex items-center gap-2 text-sm text-terminal-muted"><Spinner /> Analysing…</div>}

      {regime && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel title="Detected Regime">
            <div className="flex items-center gap-3">
              <Radar size={40} className={REGIME_COLORS[regime.regime] || "text-gold"} />
              <div>
                <div className={`text-2xl font-bold ${REGIME_COLORS[regime.regime] || "text-gold"}`}>
                  {regime.regime.replace(/_/g, " ")}
                </div>
                <div className="text-sm text-terminal-muted">Confidence: {regime.confidence}%</div>
              </div>
            </div>
            <p className="mt-3 text-xs leading-relaxed text-terminal-muted">{regime.reason}</p>
            <div className="mt-3 space-y-2">
              <div>
                <div className="mb-1 text-[10px] uppercase text-terminal-muted">Recommended</div>
                <div className="flex flex-wrap gap-1.5">
                  {regime.recommended_strategy_types.length ? regime.recommended_strategy_types.map((t: string) => <Badge key={t} tone="buy">{t}</Badge>) : <span className="text-xs text-terminal-muted">Stand aside</span>}
                </div>
              </div>
              <div>
                <div className="mb-1 text-[10px] uppercase text-terminal-muted">Avoid</div>
                <div className="flex flex-wrap gap-1.5">
                  {regime.avoid_strategy_types.map((t: string) => <Badge key={t} tone="sell">{t}</Badge>)}
                </div>
              </div>
            </div>
          </Panel>

          <Panel title="Strategy Selection">
            {selection ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <MetricCard label="Selected" value={<span className="text-base text-gold">{selection.selected_strategy || "—"}</span>} />
                  <MetricCard label="Backup" value={<span className="text-base">{selection.backup_strategy || "—"}</span>} />
                </div>
                <p className="text-xs leading-relaxed text-gray-300">{selection.reason}</p>
                <div className="rounded-md border border-warn/30 bg-warn/5 px-3 py-2 text-xs text-warn">{selection.risk_warning}</div>
                <div className="text-xs text-terminal-muted">Selection confidence: {selection.confidence}%</div>
              </div>
            ) : (
              <div className="py-6 text-center text-sm text-terminal-muted">Run "Run All" in Strategy Lab first to enable regime-aware selection.</div>
            )}
          </Panel>
        </div>
      )}
    </div>
  );
}
