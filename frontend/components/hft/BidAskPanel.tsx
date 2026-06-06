"use client";
import { Tick } from "@/lib/types";

export function BidAskPanel({ tick }: { tick?: Tick }) {
  const digits = tick && tick.mid > 50 ? 2 : 5;
  return (
    <div className="grid grid-cols-2 gap-2">
      <div className="rounded-md border border-sell/30 bg-sell/5 px-3 py-2">
        <div className="text-[10px] uppercase tracking-wider text-terminal-muted">Bid</div>
        <div className="mono text-lg font-bold text-sell">{tick ? tick.bid.toFixed(digits) : "—"}</div>
      </div>
      <div className="rounded-md border border-buy/30 bg-buy/5 px-3 py-2 text-right">
        <div className="text-[10px] uppercase tracking-wider text-terminal-muted">Ask</div>
        <div className="mono text-lg font-bold text-buy">{tick ? tick.ask.toFixed(digits) : "—"}</div>
      </div>
    </div>
  );
}
