"use client";
import { OrderState } from "@/lib/types";

export function OrderFlowPanel({ orders }: { orders: OrderState[] }) {
  const filled = orders.filter((o) => o.state === "filled");
  const rejected = orders.filter((o) => o.state === "rejected" || o.state === "expired");
  const buys = filled.filter((o) => o.side === "buy").length;
  const sells = filled.filter((o) => o.side === "sell").length;
  const total = buys + sells || 1;
  const buyPct = (buys / total) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-terminal-muted">
        <span>Buy flow {buys}</span>
        <span>Sell flow {sells}</span>
      </div>
      <div className="flex h-2.5 overflow-hidden rounded-full bg-terminal-panel">
        <div className="bg-buy" style={{ width: `${buyPct}%` }} />
        <div className="bg-sell" style={{ width: `${100 - buyPct}%` }} />
      </div>
      <div className="grid grid-cols-3 gap-2 pt-1 text-center">
        <Stat label="Filled" value={filled.length} tone="text-buy" />
        <Stat label="Rejected" value={rejected.length} tone="text-sell" />
        <Stat label="Total" value={orders.length} tone="text-gray-200" />
      </div>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: number; tone: string }) {
  return (
    <div className="rounded-md border border-terminal-border bg-terminal-panel/40 py-1.5">
      <div className={`mono text-base font-bold ${tone}`}>{value}</div>
      <div className="text-[9px] uppercase text-terminal-muted">{label}</div>
    </div>
  );
}
