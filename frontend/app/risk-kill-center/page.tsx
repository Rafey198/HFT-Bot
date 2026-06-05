"use client";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { RiskState } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel } from "@/components/ui/primitives";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RiskKillSwitch } from "@/components/hft/RiskKillSwitch";
import { StatusBadge } from "@/components/dashboard/StatusBadge";
import { WarningBanner } from "@/components/dashboard/WarningBanner";
import { fmt, fmtMoney, pctColor } from "@/lib/utils";

export default function RiskKillCenterPage() {
  const { data: risk } = usePoll<RiskState>(() => api.riskState() as Promise<RiskState>, 1000);
  const onKill = (a: boolean) => api.killSwitch({ activate: a, reason: a ? "Manual kill switch (risk center)" : "" });

  const dailyUsed = risk ? Math.min(100, (Math.abs(Math.min(0, risk.daily_pnl_percent)) / risk.max_daily_loss) * 100) : 0;
  const ddUsed = risk ? Math.min(100, (risk.drawdown_percent / risk.max_drawdown_stop) * 100) : 0;

  return (
    <div className="space-y-4 p-5">
      <PageHeader title="Risk Kill Center" subtitle="Live risk caps, exposure, and the emergency kill switch." />

      {risk?.kill_switch_active && <WarningBanner tone="danger">Execution halted by kill switch: {risk.kill_reason}</WarningBanner>}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <MetricCard label="Balance" value={fmtMoney(risk?.balance)} />
            <MetricCard label="Equity" value={fmtMoney(risk?.equity)} tone="gold" />
            <MetricCard label="Day P/L" value={<span className={pctColor(risk?.daily_pnl || 0)}>{fmt(risk?.daily_pnl_percent)}%</span>} />
            <MetricCard label="Drawdown" value={`${fmt(risk?.drawdown_percent)}%`} tone="sell" />
            <MetricCard label="Open Trades" value={risk?.open_positions ?? 0} />
            <MetricCard label="Trades Today" value={risk?.trades_today ?? 0} />
            <MetricCard label="Trades/min" value={`${risk?.trades_per_minute ?? 0}/${risk?.max_trades_per_minute ?? 0}`} />
            <MetricCard label="Loss Streak" value={risk?.consecutive_losses ?? 0} tone={(risk?.consecutive_losses ?? 0) >= 2 ? "sell" : "default"} />
          </div>

          <Panel title="Risk Limit Usage">
            <Gauge label={`Daily loss (${fmt(risk?.max_daily_loss)}% cap)`} pct={dailyUsed} />
            <Gauge label={`Max drawdown (${fmt(risk?.max_drawdown_stop)}% cap)`} pct={ddUsed} />
            <div className="mt-2 flex items-center gap-2 text-xs">
              <span className="text-terminal-muted">Auto-disable:</span>
              {risk && <StatusBadge status={risk.auto_disabled ? "blocked" : "safe"} />}
            </div>
          </Panel>
        </div>

        <Panel title="Emergency Control">
          <RiskKillSwitch risk={risk || undefined} onToggle={onKill} />
          <p className="mt-3 text-[11px] leading-relaxed text-terminal-muted">
            The risk manager overrides all signals. When daily loss or max drawdown caps are hit, the kill switch
            activates automatically, flattens positions, and blocks new orders until reset.
          </p>
        </Panel>
      </div>
    </div>
  );
}

function Gauge({ label, pct }: { label: string; pct: number }) {
  const tone = pct > 80 ? "bg-danger" : pct > 50 ? "bg-warn" : "bg-buy";
  return (
    <div className="mb-3">
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-terminal-muted">{label}</span>
        <span className="mono text-gray-200">{pct.toFixed(0)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-terminal-panel">
        <div className={`h-full rounded-full transition-all ${tone}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
