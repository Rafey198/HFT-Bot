"use client";
import { BacktestResult } from "@/lib/types";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { cn, fmt, pctColor } from "@/lib/utils";

export function StrategyLeaderboard({
  results,
  onSelect,
  selectedKey,
}: {
  results: BacktestResult[];
  onSelect?: (key: string) => void;
  selectedKey?: string;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-[10px] uppercase tracking-wider text-terminal-muted">
          <tr className="border-b border-terminal-border">
            <th className="py-2 pr-2">#</th>
            <th className="pr-2">Strategy</th>
            <th className="pr-2">Return</th>
            <th className="pr-2">PF</th>
            <th className="pr-2">DD</th>
            <th className="pr-2">Sharpe</th>
            <th className="pr-2">Trades</th>
            <th className="pr-2">Verdict</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr
              key={r.strategy_key || r.strategy_name}
              onClick={() => r.strategy_key && onSelect?.(r.strategy_key)}
              className={cn(
                "border-b border-terminal-border/50 transition-colors",
                onSelect && "cursor-pointer hover:bg-terminal-panel/60",
                selectedKey === r.strategy_key && "bg-gold/5",
              )}
            >
              <td className="mono py-2 pr-2 text-terminal-muted">{i + 1}</td>
              <td className="pr-2 font-medium text-gray-100">{r.strategy_name}</td>
              <td className={cn("mono pr-2", pctColor(r.total_return))}>{fmt(r.total_return)}%</td>
              <td className="mono pr-2">{fmt(r.profit_factor)}</td>
              <td className="mono pr-2 text-warn">{fmt(r.max_drawdown)}%</td>
              <td className="mono pr-2">{fmt(r.sharpe)}</td>
              <td className="mono pr-2 text-terminal-muted">{r.num_trades}</td>
              <td className="pr-2"><StatusBadge status={r.recommendation} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      {!results.length && <div className="py-6 text-center text-xs text-terminal-muted">Run all strategies to populate the leaderboard.</div>}
    </div>
  );
}
