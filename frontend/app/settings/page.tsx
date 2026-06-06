"use client";
import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { api, API_BASE } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button } from "@/components/ui/primitives";
import { WarningBanner } from "@/components/dashboard/WarningBanner";

const FIELDS: { key: string; label: string; step?: number }[] = [
  { key: "initial_balance", label: "Initial balance ($)", step: 100 },
  { key: "risk_per_trade", label: "Risk per trade (%)", step: 0.05 },
  { key: "max_daily_loss", label: "Max daily loss (%)", step: 0.5 },
  { key: "max_weekly_loss", label: "Max weekly loss (%)", step: 0.5 },
  { key: "max_drawdown_stop", label: "Max drawdown stop (%)", step: 0.5 },
  { key: "max_trades_per_minute", label: "Max trades / minute", step: 1 },
  { key: "max_trades_per_day", label: "Max trades / day", step: 1 },
  { key: "max_consecutive_losses", label: "Max consecutive losses", step: 1 },
  { key: "max_open_positions", label: "Max open positions", step: 1 },
  { key: "min_reward_risk", label: "Min reward:risk", step: 0.1 },
  { key: "max_spread_points", label: "Max spread (points)", step: 1 },
  { key: "min_signal_confidence", label: "Min signal confidence", step: 1 },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, number>>({});
  const [saved, setSaved] = useState(false);
  const [endpoint, setEndpoint] = useState(API_BASE);

  useEffect(() => { api.riskSettings().then((s: any) => setSettings(s)).catch(() => {}); }, []);

  const save = async () => {
    try {
      await api.updateRiskSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch { /* ignore */ }
  };

  return (
    <div className="space-y-4 p-5">
      <PageHeader title="Settings" subtitle="Risk defaults, replay, broker, and API configuration." right={<Button variant="gold" onClick={save}><Save size={14} /> Save Risk Settings</Button>} />

      {saved && <WarningBanner tone="info">Risk settings saved and applied to the live engine.</WarningBanner>}

      <Panel title="Risk Defaults">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {FIELDS.map((f) => (
            <label key={f.key} className="text-xs">
              <span className="text-terminal-muted">{f.label}</span>
              <input
                type="number"
                step={f.step}
                value={settings[f.key] ?? ""}
                onChange={(e) => setSettings((p) => ({ ...p, [f.key]: parseFloat(e.target.value) }))}
                className="mono mt-1 w-full rounded-md border border-terminal-border bg-terminal-panel px-3 py-2 outline-none focus:border-gold/50"
              />
            </label>
          ))}
        </div>
      </Panel>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="API Endpoint">
          <label className="text-xs">
            <span className="text-terminal-muted">Backend base URL (set via NEXT_PUBLIC_API_BASE)</span>
            <input value={endpoint} onChange={(e) => setEndpoint(e.target.value)} disabled className="mono mt-1 w-full rounded-md border border-terminal-border bg-terminal-panel px-3 py-2 text-terminal-muted" />
          </label>
          <p className="mt-2 text-[11px] text-terminal-muted">Configure at build/run time with the NEXT_PUBLIC_API_BASE environment variable.</p>
        </Panel>
        <Panel title="Broker (placeholder)">
          <div className="space-y-2 text-xs text-terminal-muted">
            <div className="flex justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2"><span>Broker</span><span className="text-gray-300">Paper (simulated)</span></div>
            <div className="flex justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2"><span>MetaTrader 5</span><span className="text-warn">Not installed / locked</span></div>
            <div className="flex justify-between rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2"><span>Live trading</span><span className="text-danger">Disabled by default</span></div>
          </div>
        </Panel>
      </div>

      <Panel title="Replay & Slippage Defaults">
        <div className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
          <Def label="Default speed" value="10x" />
          <Def label="Speeds" value="1 / 5 / 10 / 50 / 100x" />
          <Def label="Default spread" value="20 points (XAUUSD)" />
          <Def label="Slippage model" value="latency-scaled" />
        </div>
      </Panel>
    </div>
  );
}

function Def({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-terminal-border bg-terminal-panel/40 px-3 py-2">
      <div className="text-[10px] uppercase text-terminal-muted">{label}</div>
      <div className="mono text-sm text-gray-200">{value}</div>
    </div>
  );
}
