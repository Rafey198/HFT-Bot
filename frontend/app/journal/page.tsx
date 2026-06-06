"use client";
import { useState } from "react";
import { Download } from "lucide-react";
import { api, API_BASE } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button } from "@/components/ui/primitives";
import { cn, timeShort } from "@/lib/utils";

const TYPE_COLORS: Record<string, string> = {
  open: "text-buy", close: "text-gold", blocked: "text-warn", signal: "text-terminal-muted",
};

export default function JournalPage() {
  const { data } = usePoll<any>(() => api.journal(), 2000);
  const [filter, setFilter] = useState("all");
  const events = (data?.events || []).filter((e: any) => filter === "all" || e.type === filter);

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Trade Journal"
        subtitle="All signals, blocked trades, opens, and closes with full context."
        right={
          <div className="flex items-center gap-2">
            <select value={filter} onChange={(e) => setFilter(e.target.value)} className="rounded-md border border-terminal-border bg-terminal-panel px-2 py-1.5 text-xs text-gray-200">
              {["all", "signal", "open", "close", "blocked"].map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <a href={`${API_BASE}/api/journal/export?fmt=csv`} target="_blank" rel="noreferrer"><Button size="sm"><Download size={13} /> CSV</Button></a>
            <a href={`${API_BASE}/api/journal/export?fmt=json`} target="_blank" rel="noreferrer"><Button size="sm" variant="ghost">JSON</Button></a>
          </div>
        }
      />

      <Panel title={`Events (${events.length})`}>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[10px] uppercase text-terminal-muted">
              <tr className="border-b border-terminal-border">
                <th className="py-1.5 pr-3">Time</th><th className="pr-3">Type</th><th className="pr-3">Side</th>
                <th className="pr-3">Strategy</th><th className="pr-3">Regime</th><th className="pr-3">Detail</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e: any, i: number) => (
                <tr key={i} className="border-b border-terminal-border/40">
                  <td className="mono py-1.5 pr-3 text-terminal-muted">{timeShort(e.ts)}</td>
                  <td className={cn("pr-3 font-semibold uppercase", TYPE_COLORS[e.type])}>{e.type}</td>
                  <td className={cn("pr-3 uppercase", e.side === "buy" ? "text-buy" : e.side === "sell" ? "text-sell" : "text-terminal-muted")}>{e.side || "—"}</td>
                  <td className="pr-3 text-gray-300">{e.strategy || "—"}</td>
                  <td className="pr-3 text-terminal-muted">{e.regime || "—"}</td>
                  <td className="pr-3 text-terminal-muted">
                    {e.type === "close" ? <span className={e.pnl >= 0 ? "text-buy" : "text-sell"}>P/L {e.pnl} ({e.reason})</span> :
                     e.type === "open" ? <span className="mono">@{e.entry_price} · {e.lot_size} lots</span> :
                     e.reason || e.confidence}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!events.length && <div className="py-6 text-center text-sm text-terminal-muted">No journal events yet. Start a replay to populate.</div>}
        </div>
      </Panel>
    </div>
  );
}
