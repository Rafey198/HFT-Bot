"use client";
import { Position } from "@/lib/types";
import { cn, fmtMoney, timeShort } from "@/lib/utils";

export function ClosedTradesPanel({ trades }: { trades: Position[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-[10px] uppercase tracking-wider text-terminal-muted">
          <tr className="border-b border-terminal-border">
            <th className="py-1.5 pr-2">Side</th>
            <th className="pr-2">Entry</th>
            <th className="pr-2">Exit</th>
            <th className="pr-2">P/L</th>
            <th className="pr-2">Reason</th>
            <th className="pr-2">Time</th>
          </tr>
        </thead>
        <tbody>
          {[...trades].reverse().slice(0, 30).map((p) => (
            <tr key={p.trade_id} className="border-b border-terminal-border/50">
              <td className={cn("py-1.5 pr-2 font-semibold uppercase", p.side === "buy" ? "text-buy" : "text-sell")}>{p.side}</td>
              <td className="mono pr-2">{p.entry_price.toFixed(2)}</td>
              <td className="mono pr-2">{p.exit_price.toFixed(2)}</td>
              <td className={cn("mono pr-2 font-semibold", p.pnl >= 0 ? "text-buy" : "text-sell")}>{fmtMoney(p.pnl)}</td>
              <td className="pr-2 text-terminal-muted">{p.reason}</td>
              <td className="mono pr-2 text-terminal-muted">{timeShort(p.exit_time)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!trades.length && <div className="py-5 text-center text-xs text-terminal-muted">No closed trades yet.</div>}
    </div>
  );
}
