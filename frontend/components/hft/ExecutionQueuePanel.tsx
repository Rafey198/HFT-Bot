"use client";
import { motion } from "framer-motion";
import { OrderState } from "@/lib/types";
import { cn, timeShort } from "@/lib/utils";

const STATE_COLORS: Record<string, string> = {
  filled: "text-buy border-buy/40 bg-buy/10",
  rejected: "text-sell border-sell/40 bg-sell/10",
  expired: "text-warn border-warn/40 bg-warn/10",
  cancelled: "text-terminal-muted border-terminal-border",
  queued: "text-gold border-gold/40 bg-gold/10",
  executing: "text-gold border-gold/40 bg-gold/10",
};

export function ExecutionQueuePanel({ orders }: { orders: OrderState[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-[10px] uppercase tracking-wider text-terminal-muted">
          <tr className="border-b border-terminal-border">
            <th className="py-1.5 pr-2">Order</th>
            <th className="pr-2">Side</th>
            <th className="pr-2">Req</th>
            <th className="pr-2">Fill</th>
            <th className="pr-2">Lat</th>
            <th className="pr-2">Slip</th>
            <th className="pr-2">State</th>
          </tr>
        </thead>
        <tbody>
          {orders.slice(0, 14).map((o) => (
            <motion.tr
              key={o.order_id}
              initial={{ opacity: 0, backgroundColor: "rgba(245,196,81,0.08)" }}
              animate={{ opacity: 1, backgroundColor: "rgba(0,0,0,0)" }}
              className="border-b border-terminal-border/50"
            >
              <td className="mono py-1.5 pr-2 text-terminal-muted">{o.order_id.slice(-6)}</td>
              <td className={cn("pr-2 font-semibold uppercase", o.side === "buy" ? "text-buy" : "text-sell")}>{o.side}</td>
              <td className="mono pr-2">{o.requested_price.toFixed(2)}</td>
              <td className="mono pr-2">{o.filled_price ? o.filled_price.toFixed(2) : "—"}</td>
              <td className="mono pr-2 text-terminal-muted">{o.latency_ms.toFixed(0)}</td>
              <td className="mono pr-2 text-terminal-muted">{o.slippage ? o.slippage.toFixed(3) : "—"}</td>
              <td className="pr-2">
                <span className={cn("rounded border px-1.5 py-0.5 text-[10px] font-semibold", STATE_COLORS[o.state] || "text-terminal-muted border-terminal-border")}>
                  {o.state}
                </span>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
      {!orders.length && <div className="py-6 text-center text-xs text-terminal-muted">No orders in queue.</div>}
    </div>
  );
}
