"use client";
import { Latency } from "@/lib/types";
import { StatusBadge } from "@/components/dashboard/StatusBadge";

const ROWS: { key: keyof Latency; label: string }[] = [
  { key: "market_feed_latency_ms", label: "Market feed" },
  { key: "signal_latency_ms", label: "Signal" },
  { key: "risk_latency_ms", label: "Risk check" },
  { key: "execution_latency_ms", label: "Exec queue" },
  { key: "broker_latency_ms", label: "Broker" },
];

export function LatencyMeter({ latency }: { latency?: Latency }) {
  return (
    <div className="rounded-md border border-terminal-border px-3 py-2">
      <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-wider text-terminal-muted">
        <span>Latency</span>
        {latency && <StatusBadge status={latency.status} />}
      </div>
      <div className="space-y-1">
        {ROWS.map((r) => {
          const v = latency ? (latency[r.key] as number) : 0;
          const pct = Math.min(100, (v / 50) * 100);
          return (
            <div key={r.key} className="flex items-center gap-2">
              <span className="w-20 text-[10px] text-terminal-muted">{r.label}</span>
              <div className="h-1 flex-1 overflow-hidden rounded-full bg-terminal-panel">
                <div className="h-full rounded-full bg-gold/70" style={{ width: `${pct}%` }} />
              </div>
              <span className="mono w-12 text-right text-[10px] text-gray-300">{v.toFixed(1)}ms</span>
            </div>
          );
        })}
      </div>
      <div className="mt-2 flex items-center justify-between border-t border-terminal-border pt-1.5">
        <span className="text-[10px] uppercase text-terminal-muted">Round-trip</span>
        <span className="mono text-sm font-bold text-gold">{latency ? latency.total_latency_ms.toFixed(1) : "—"} ms</span>
      </div>
    </div>
  );
}
