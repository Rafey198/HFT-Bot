"use client";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { PageHeader } from "@/components/PageHeader";
import { Panel } from "@/components/ui/primitives";
import { Check, X, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ExplainabilityPage() {
  const { data } = usePoll<any>(() => api.explain(), 2000);
  const exp = data?.explanation;
  const signal = data?.signal;
  const risk = data?.risk_check;

  return (
    <div className="space-y-4 p-5">
      <PageHeader title="Explainability" subtitle="Plain-English rationale for the latest actionable signal." />

      {!exp ? (
        <Panel><div className="py-10 text-center text-sm text-terminal-muted">No actionable signal yet. Start a replay to generate explainable signals.</div></Panel>
      ) : (
        <>
          <Panel title={`Signal — ${signal?.strategy} (${signal?.side?.toUpperCase()})`}>
            <p className="text-sm leading-relaxed text-gray-200">{exp.plain_english_reason}</p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="chip">Entry <span className="mono ml-1 text-gold">{signal?.entry}</span></span>
              <span className="chip">SL <span className="mono ml-1 text-sell">{signal?.stop_loss}</span></span>
              <span className="chip">TP <span className="mono ml-1 text-buy">{signal?.take_profit}</span></span>
              <span className="chip">Confidence <span className="mono ml-1">{signal?.confidence}</span></span>
            </div>
          </Panel>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Panel title="Indicator Votes">
              <div className="space-y-1.5">
                {exp.indicator_votes?.length ? exp.indicator_votes.map((v: any, i: number) => (
                  <div key={i} className="flex items-center justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-1.5 text-xs">
                    <span className="flex items-center gap-2">
                      {v.agrees ? <Check size={13} className="text-buy" /> : <X size={13} className="text-sell" />}
                      <span className="text-gray-200">{v.indicator}</span>
                    </span>
                    <span className="mono text-terminal-muted">{String(v.value)}</span>
                  </div>
                )) : <div className="text-xs text-terminal-muted">Tick-level signal — indicator votes available on candle strategies.</div>}
              </div>
            </Panel>

            <Panel title="Risk Notes">
              <ul className="space-y-1.5 text-xs">
                {exp.risk_notes?.map((n: string, i: number) => (
                  <li key={i} className="flex gap-2 text-gray-300"><span className="text-gold">•</span> {n}</li>
                ))}
              </ul>
              {risk && (
                <div className={cn("mt-2 rounded-md border px-2 py-1 text-[11px]", risk.trade_allowed ? "border-buy/30 text-buy" : "border-warn/30 text-warn")}>
                  Risk manager: {risk.risk_status} · lot {risk.lot_size} {risk.blocked_by?.length ? `· blocked: ${risk.blocked_by.join(", ")}` : ""}
                </div>
              )}
            </Panel>

            <Panel title="What Could Go Wrong">
              <ul className="space-y-1.5 text-xs">
                {exp.what_could_go_wrong?.map((n: string, i: number) => (
                  <li key={i} className="flex gap-2 text-terminal-muted"><AlertTriangle size={12} className="mt-0.5 shrink-0 text-warn" /> {n}</li>
                ))}
              </ul>
            </Panel>
          </div>
        </>
      )}
    </div>
  );
}
