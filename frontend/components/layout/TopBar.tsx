"use client";
import { usePoll } from "@/lib/usePoll";
import { api } from "@/lib/api";
import { RiskState } from "@/lib/types";
import { fmtMoney, pctColor, fmt } from "@/lib/utils";
import { Activity, Lock } from "lucide-react";

export function TopBar() {
  const { data: risk } = usePoll<RiskState>(() => api.riskState() as Promise<RiskState>, 2000);

  return (
    <header className="flex h-12 shrink-0 items-center justify-between border-b border-terminal-border bg-terminal-panel/60 px-4">
      <div className="flex items-center gap-3">
        <div className="md:hidden text-sm font-bold text-gold">AurumFX</div>
        <span className="chip border-gold/30 text-gold">
          <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-gold" /> XAUUSD focus
        </span>
        <span className="hidden text-xs text-terminal-muted sm:inline">
          HFT-style retail quant execution simulator
        </span>
      </div>
      <div className="flex items-center gap-3 text-xs">
        {risk && (
          <>
            <div className="hidden items-center gap-1.5 sm:flex">
              <span className="text-terminal-muted">Equity</span>
              <span className="mono font-semibold text-gray-100">{fmtMoney(risk.equity)}</span>
            </div>
            <div className="hidden items-center gap-1.5 sm:flex">
              <span className="text-terminal-muted">Day P/L</span>
              <span className={`mono font-semibold ${pctColor(risk.daily_pnl)}`}>
                {fmt(risk.daily_pnl_percent)}%
              </span>
            </div>
            {risk.kill_switch_active ? (
              <span className="chip border-danger/50 bg-danger/15 text-danger">
                <Lock size={12} /> KILLED
              </span>
            ) : (
              <span className="chip border-buy/40 bg-buy/10 text-buy">
                <Activity size={12} /> ARMED
              </span>
            )}
          </>
        )}
        <span className="chip border-terminal-border text-terminal-muted">LIVE: OFF</span>
      </div>
    </header>
  );
}
