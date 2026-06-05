"use client";
import { Latency, ReplayState, RiskState, Tick } from "@/lib/types";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { fmtMoney, pctColor, fmt, timeShort } from "@/lib/utils";

export function HftStatusBar({
  tick,
  latency,
  risk,
  state,
}: {
  tick?: Tick;
  latency?: Latency;
  risk?: RiskState;
  state?: ReplayState;
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2 rounded-md border border-terminal-border bg-terminal-panel/60 px-4 py-2 text-xs">
      <Item label="Symbol" value={<span className="text-gold">{tick?.symbol || state?.symbol || "XAUUSD"}</span>} />
      <Item label="Clock" value={<span className="mono">{timeShort(state?.clock || "")}</span>} />
      <Item label="Feed" value={<span className="text-gray-300">{state?.source || "—"}</span>} />
      <Item label="Speed" value={<span className="mono">{state?.speed || 1}x</span>} />
      <Item label="Latency" value={latency ? <StatusBadge status={latency.status} /> : "—"} />
      <Item label="Equity" value={<span className="mono">{fmtMoney(risk?.equity)}</span>} />
      <Item label="Day P/L" value={<span className={`mono ${pctColor(risk?.daily_pnl || 0)}`}>{fmt(risk?.daily_pnl_percent)}%</span>} />
      <Item label="Open" value={<span className="mono">{risk?.open_positions ?? 0}</span>} />
      <Item label="Risk" value={risk ? <StatusBadge status={risk.risk_status} /> : "—"} />
      <div className="ml-auto flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${state?.running && !state.paused ? "bg-buy animate-pulseDot" : "bg-terminal-muted"}`} />
        <span className="text-terminal-muted">{state?.running ? (state.paused ? "Paused" : "Streaming") : "Idle"}</span>
      </div>
    </div>
  );
}

function Item({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-[10px] uppercase tracking-wider text-terminal-muted">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}
