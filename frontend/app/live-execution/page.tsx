"use client";
import { useEffect, useState } from "react";
import { Lock, Unlock, Check, X } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button } from "@/components/ui/primitives";
import { Disclaimer } from "@/components/dashboard/Disclaimer";
import { WarningBanner } from "@/components/dashboard/WarningBanner";
import { cn } from "@/lib/utils";

const PHRASE = "I understand this can lose money";

export default function LiveExecutionPage() {
  const [liveEnabled, setLiveEnabled] = useState(false);
  const [phrase, setPhrase] = useState("");
  const [brokerConnected, setBrokerConnected] = useState(false);
  const [result, setResult] = useState<any>(null);

  const check = async () => {
    try {
      const r = await api.liveCheck({ live_mode_enabled: liveEnabled, confirmation_phrase: phrase, broker_connected: brokerConnected });
      setResult(r);
    } catch { /* ignore */ }
  };

  useEffect(() => { check(); /* eslint-disable-next-line */ }, [liveEnabled, phrase, brokerConnected]);

  const allowed = result?.live_allowed;

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Live Execution"
        subtitle="Locked by default. All safety conditions must pass to unlock real trading."
        right={
          <span className={cn("chip", allowed ? "border-buy/50 text-buy" : "border-danger/50 text-danger")}>
            {allowed ? <Unlock size={12} /> : <Lock size={12} />} {allowed ? "UNLOCKED" : "LOCKED"}
          </span>
        }
      />

      <Disclaimer />
      <WarningBanner tone="danger">
        Live trading is disabled by default. Even when all checks pass, this demo will not place real orders unless a
        real MetaTrader 5 terminal is installed and explicitly approved by the risk manager. Always paper trade first.
      </WarningBanner>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Unlock Requirements">
          <div className="space-y-3">
            <label className="flex items-center justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2 text-sm">
              <span className="text-gray-300">Enable Live Mode toggle</span>
              <input type="checkbox" checked={liveEnabled} onChange={(e) => setLiveEnabled(e.target.checked)} />
            </label>
            <div>
              <div className="mb-1 text-xs text-terminal-muted">Type confirmation phrase exactly:</div>
              <div className="mono mb-1 text-[11px] text-gold">{PHRASE}</div>
              <input
                value={phrase}
                onChange={(e) => setPhrase(e.target.value)}
                placeholder="Type the phrase…"
                className="mono w-full rounded-md border border-terminal-border bg-terminal-panel px-3 py-2 text-sm outline-none focus:border-gold/50"
              />
            </div>
            <label className="flex items-center justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2 text-sm">
              <span className="text-gray-300">Broker connection verified</span>
              <input type="checkbox" checked={brokerConnected} onChange={(e) => setBrokerConnected(e.target.checked)} />
            </label>
            {result?.mt5 && !result.mt5.available && (
              <WarningBanner>MetaTrader5 package not installed — broker stays simulated/locked.</WarningBanner>
            )}
          </div>
        </Panel>

        <Panel title="Safety Checklist">
          <div className="space-y-1.5">
            {result?.checklist?.map((c: any) => (
              <div key={c.name} className="flex items-start gap-2 rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2 text-xs">
                {c.passed ? <Check size={14} className="mt-0.5 shrink-0 text-buy" /> : <X size={14} className="mt-0.5 shrink-0 text-danger" />}
                <div>
                  <div className={c.passed ? "text-gray-200" : "text-gray-400"}>{c.name}</div>
                  {c.detail && <div className="text-[10px] text-terminal-muted">{c.detail}</div>}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3">
            <Button variant={allowed ? "buy" : "ghost"} disabled={!allowed} className="w-full">
              {allowed ? "Live trading conditions met (still simulated)" : "Live execution blocked"}
            </Button>
          </div>
        </Panel>
      </div>

      <Panel title="Live Execution Logs">
        <div className="py-6 text-center text-xs text-terminal-muted">
          No live orders. Live execution remains locked — this is a research simulator.
        </div>
      </Panel>
    </div>
  );
}
