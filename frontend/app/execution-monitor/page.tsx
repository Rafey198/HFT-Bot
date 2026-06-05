"use client";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { Latency, OrderState } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel } from "@/components/ui/primitives";
import { ExecutionQueuePanel } from "@/components/hft/ExecutionQueuePanel";
import { LatencyMeter } from "@/components/hft/LatencyMeter";
import { OrderFlowPanel } from "@/components/hft/OrderFlowPanel";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { fmt } from "@/lib/utils";

export default function ExecutionMonitorPage() {
  const { data: queueRes } = usePoll<{ orders: OrderState[] }>(() => api.executionQueue(), 900);
  const { data: latency } = usePoll<Latency>(() => api.latency() as Promise<Latency>, 1200);
  const orders = queueRes?.orders || [];
  const filled = orders.filter((o) => o.state === "filled");
  const avgSlip = filled.length ? filled.reduce((a, o) => a + o.slippage, 0) / filled.length : 0;
  const avgLat = filled.length ? filled.reduce((a, o) => a + o.latency_ms, 0) / filled.length : 0;
  const rejects = orders.filter((o) => o.state !== "filled");

  const reasonCounts: Record<string, number> = {};
  rejects.forEach((o) => { reasonCounts[o.reason] = (reasonCounts[o.reason] || 0) + 1; });

  return (
    <div className="space-y-4 p-5">
      <PageHeader title="Execution Monitor" subtitle="Order state transitions, latency breakdown, fill quality, and rejections." />

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <MetricCard label="Orders" value={orders.length} />
        <MetricCard label="Fill rate" value={`${orders.length ? fmt((filled.length / orders.length) * 100) : 0}%`} tone="buy" />
        <MetricCard label="Avg latency" value={`${fmt(avgLat)} ms`} />
        <MetricCard label="Avg slippage" value={fmt(avgSlip, 4)} tone="gold" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Panel title="Latency Breakdown" className="lg:col-span-1"><LatencyMeter latency={latency || undefined} /></Panel>
        <Panel title="Order Flow" className="lg:col-span-1"><OrderFlowPanel orders={orders} /></Panel>
        <Panel title="Rejection Reasons" className="lg:col-span-1">
          <div className="space-y-1.5">
            {Object.entries(reasonCounts).length ? Object.entries(reasonCounts).map(([r, c]) => (
              <div key={r} className="flex items-center justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-2 py-1 text-xs">
                <span className="text-warn">{r}</span>
                <span className="mono text-gray-200">{c}</span>
              </div>
            )) : <div className="py-4 text-center text-xs text-terminal-muted">No rejections.</div>}
          </div>
        </Panel>
      </div>

      <Panel title="Order Queue — State Transitions"><ExecutionQueuePanel orders={orders} /></Panel>
    </div>
  );
}
