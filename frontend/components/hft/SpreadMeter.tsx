"use client";
import { Tick } from "@/lib/types";
import { cn } from "@/lib/utils";

export function SpreadMeter({ tick, maxSpreadPoints = 30 }: { tick?: Tick; maxSpreadPoints?: number }) {
  // Estimate points from spread using a heuristic point size.
  const point = tick && tick.mid > 50 ? 0.01 : 0.00001;
  const spreadPoints = tick ? tick.spread / point : 0;
  const pct = Math.min(100, (spreadPoints / maxSpreadPoints) * 100);
  const tone = spreadPoints > maxSpreadPoints ? "bg-danger" : spreadPoints > maxSpreadPoints * 0.7 ? "bg-warn" : "bg-buy";
  return (
    <div className="rounded-md border border-terminal-border px-3 py-2">
      <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-terminal-muted">
        <span>Spread</span>
        <span className="mono text-gray-200">{spreadPoints.toFixed(1)} pts</span>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-terminal-panel">
        <div className={cn("h-full rounded-full transition-all duration-300", tone)} style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-1 text-right text-[9px] text-terminal-muted">max {maxSpreadPoints} pts</div>
    </div>
  );
}
