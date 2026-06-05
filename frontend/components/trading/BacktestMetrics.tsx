"use client";
import { BacktestResult } from "@/lib/types";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { fmt, pctColor } from "@/lib/utils";

export function BacktestMetrics({ r }: { r: BacktestResult }) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
      <MetricCard label="Total Return" value={<span className={pctColor(r.total_return)}>{fmt(r.total_return)}%</span>} />
      <MetricCard label="CAGR" value={`${fmt(r.cagr)}%`} />
      <MetricCard label="Win Rate" value={`${fmt(r.win_rate)}%`} />
      <MetricCard label="Profit Factor" value={fmt(r.profit_factor)} tone={r.profit_factor >= 1.2 ? "buy" : "sell"} />
      <MetricCard label="Max Drawdown" value={`${fmt(r.max_drawdown)}%`} tone="sell" />
      <MetricCard label="Sharpe" value={fmt(r.sharpe)} />
      <MetricCard label="Sortino" value={fmt(r.sortino)} />
      <MetricCard label="Calmar" value={fmt(r.calmar)} />
      <MetricCard label="Expectancy" value={`$${fmt(r.expectancy)}`} />
      <MetricCard label="Risk:Reward" value={fmt(r.risk_reward)} />
      <MetricCard label="Trades" value={r.num_trades} />
      <MetricCard label="Recommendation" value={<StatusBadge status={r.recommendation} />} />
    </div>
  );
}
