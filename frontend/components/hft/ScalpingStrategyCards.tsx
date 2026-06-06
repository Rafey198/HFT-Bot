"use client";
import { cn } from "@/lib/utils";

interface ScalpStat {
  key: string;
  name: string;
  enabled: boolean;
  signal_count: number;
  trades: number;
  win_rate: number;
  profit_factor: number;
  avg_hold: number;
  max_drawdown: number;
  reject_reason: string;
}

export function ScalpingStrategyCards({ stats, onToggle }: { stats: ScalpStat[]; onToggle?: (key: string) => void }) {
  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-2">
      {stats.map((s) => (
        <div
          key={s.key}
          className={cn(
            "rounded-md border px-3 py-2",
            s.enabled ? "border-gold/30 bg-terminal-card" : "border-terminal-border bg-terminal-panel/40 opacity-70",
          )}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-100">{s.name}</span>
            {onToggle ? (
              <button
                onClick={() => onToggle(s.key)}
                className={cn(
                  "rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase",
                  s.enabled ? "border border-buy/40 text-buy" : "border border-terminal-border text-terminal-muted",
                )}
              >
                {s.enabled ? "On" : "Off"}
              </button>
            ) : (
              <span className={cn("h-2 w-2 rounded-full", s.enabled ? "bg-buy animate-pulseDot" : "bg-terminal-muted")} />
            )}
          </div>
          <div className="mt-2 grid grid-cols-4 gap-1 text-center">
            <Mini label="Signals" value={s.signal_count} />
            <Mini label="Trades" value={s.trades} />
            <Mini label="Win%" value={s.win_rate} />
            <Mini label="PF" value={s.profit_factor} />
          </div>
          {s.reject_reason && <div className="mt-1 text-[10px] text-warn">{s.reject_reason}</div>}
        </div>
      ))}
    </div>
  );
}

function Mini({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mono text-sm font-semibold text-gray-200">{value}</div>
      <div className="text-[9px] uppercase text-terminal-muted">{label}</div>
    </div>
  );
}
