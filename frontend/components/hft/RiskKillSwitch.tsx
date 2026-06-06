"use client";
import { useState } from "react";
import { Siren } from "lucide-react";
import { RiskState } from "@/lib/types";
import { cn } from "@/lib/utils";

export function RiskKillSwitch({ risk, onToggle }: { risk?: RiskState; onToggle: (activate: boolean) => void }) {
  const [confirming, setConfirming] = useState(false);
  const active = risk?.kill_switch_active;

  return (
    <div className={cn("rounded-md border p-3", active ? "border-danger bg-danger/10" : "border-danger/40 bg-danger/5")}>
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-danger">
        <Siren size={14} className={active ? "animate-pulseDot" : ""} /> Kill Switch
      </div>
      {active ? (
        <>
          <div className="mb-2 text-xs text-danger">{risk?.kill_reason || "Execution halted."}</div>
          <button
            onClick={() => onToggle(false)}
            className="w-full rounded-md border border-terminal-border bg-terminal-panel py-2 text-xs font-semibold text-gray-200 hover:border-gold/50"
          >
            Reset & Re-arm
          </button>
        </>
      ) : confirming ? (
        <div className="space-y-1.5">
          <div className="text-[11px] text-terminal-muted">Flatten all positions and halt execution?</div>
          <div className="flex gap-2">
            <button onClick={() => { onToggle(true); setConfirming(false); }} className="flex-1 rounded-md bg-danger py-2 text-xs font-bold text-white hover:bg-danger/80">
              CONFIRM KILL
            </button>
            <button onClick={() => setConfirming(false)} className="rounded-md border border-terminal-border px-3 text-xs text-terminal-muted">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setConfirming(true)}
          className="w-full rounded-md border-2 border-danger bg-danger/20 py-2.5 text-sm font-bold uppercase tracking-wider text-white transition-colors hover:bg-danger/40"
        >
          ⛔ Emergency Stop
        </button>
      )}
    </div>
  );
}
