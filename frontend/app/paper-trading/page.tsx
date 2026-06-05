"use client";
import { useCallback } from "react";
import { Play, Square } from "lucide-react";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button } from "@/components/ui/primitives";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { OpenPositionsPanel } from "@/components/hft/OpenPositionsPanel";
import { ClosedTradesPanel } from "@/components/hft/ClosedTradesPanel";
import { SignalScannerFeed } from "@/components/hft/SignalScannerFeed";
import { ExecutionLog } from "@/components/hft/ExecutionLog";
import { Disclaimer } from "@/components/dashboard/Disclaimer";
import { fmtMoney, pctColor, fmt } from "@/lib/utils";

export default function PaperTradingPage() {
  const { data: paper } = usePoll<any>(() => api.paperState(), 1200);
  const broker = paper?.broker;
  const risk = paper?.risk;
  const closed = broker?.closed_trades || [];
  const wins = closed.filter((t: any) => t.pnl > 0).length;
  const winRate = closed.length ? (wins / closed.length) * 100 : 0;

  const start = useCallback(() => api.paperStart({ symbol: "XAUUSD", timeframe: "M5", speed: 10 }), []);

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Paper Trading"
        subtitle="Risk-free simulated execution with full account tracking."
        right={
          <div className="flex gap-2">
            <Button variant="gold" onClick={start}><Play size={14} /> Start Paper Session</Button>
            <Button onClick={() => api.paperStop()}><Square size={14} /> Stop</Button>
          </div>
        }
      />
      <Disclaimer compact />

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        <MetricCard label="Balance" value={fmtMoney(broker?.balance)} />
        <MetricCard label="Equity" value={fmtMoney(broker?.equity)} tone="gold" />
        <MetricCard label="Open" value={broker?.open_count ?? 0} />
        <MetricCard label="Closed" value={broker?.closed_count ?? 0} />
        <MetricCard label="Win Rate" value={`${fmt(winRate)}%`} tone={winRate >= 50 ? "buy" : "sell"} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Panel title={`Open Positions (${broker?.open_count ?? 0})`} className="lg:col-span-2">
          <OpenPositionsPanel positions={broker?.open_positions || []} onClose={(id) => api.closeOrder({ trade_id: id })} />
        </Panel>
        <Panel title="Signal Feed">
          <SignalScannerFeed signals={paper?.recent_signals || []} />
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title={`Closed Trades (${closed.length})`}><ClosedTradesPanel trades={closed} /></Panel>
        <Panel title="Paper Execution Log"><div className="h-72"><ExecutionLog logs={paper?.logs || []} /></div></Panel>
      </div>
    </div>
  );
}
