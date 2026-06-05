"use client";
import { Position } from "@/lib/types";
import { cn, fmtMoney } from "@/lib/utils";

export function OpenPositionsPanel({ positions, onClose }: { positions: Position[]; onClose?: (id: string) => void }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-[10px] uppercase tracking-wider text-terminal-muted">
          <tr className="border-b border-terminal-border">
            <th className="py-1.5 pr-2">Side</th>
            <th className="pr-2">Entry</th>
            <th className="pr-2">SL</th>
            <th className="pr-2">TP</th>
            <th className="pr-2">Lots</th>
            <th className="pr-2">Strategy</th>
            {onClose && <th />}
          </tr>
        </thead>
        <tbody>
          {positions.map((p) => (
            <tr key={p.trade_id} className="border-b border-terminal-border/50">
              <td className={cn("py-1.5 pr-2 font-semibold uppercase", p.side === "buy" ? "text-buy" : "text-sell")}>{p.side}</td>
              <td className="mono pr-2">{p.entry_price.toFixed(2)}</td>
              <td className="mono pr-2 text-sell">{p.stop_loss.toFixed(2)}</td>
              <td className="mono pr-2 text-buy">{p.take_profit.toFixed(2)}</td>
              <td className="mono pr-2">{p.lot_size.toFixed(2)}</td>
              <td className="pr-2 text-terminal-muted">{p.strategy}</td>
              {onClose && (
                <td>
                  <button onClick={() => onClose(p.trade_id)} className="rounded border border-sell/40 px-1.5 py-0.5 text-[10px] text-sell hover:bg-sell/10">
                    Close
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
      {!positions.length && <div className="py-5 text-center text-xs text-terminal-muted">No open positions.</div>}
    </div>
  );
}
