"use client";
import { useState } from "react";
import { Play } from "lucide-react";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button } from "@/components/ui/primitives";
import { ScalpingStrategyCards } from "@/components/hft/ScalpingStrategyCards";
import { Disclaimer } from "@/components/dashboard/Disclaimer";

export default function ScalpingLabPage() {
  const { data } = usePoll<any>(() => api.scalpingStats(), 1500);
  const [disabled, setDisabled] = useState<Record<string, boolean>>({});

  const stats = (data?.strategies || []).map((s: any) => ({ ...s, enabled: !disabled[s.key] }));

  const toggle = (key: string) => setDisabled((p) => ({ ...p, [key]: !p[key] }));

  const restart = async () => {
    const enabled = stats.filter((s: any) => s.enabled).map((s: any) => s.key);
    await api.replayStart({ symbol: "XAUUSD", timeframe: "M5", speed: 20, auto_execute: true, enabled_scalping: enabled });
  };

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Scalping Lab"
        subtitle="10 fast scalping strategies running on the tick replay feed."
        right={<Button variant="gold" onClick={restart}><Play size={14} /> Restart with selection</Button>}
      />
      <Disclaimer compact />
      <Panel title="Fast Scalping Strategies">
        <ScalpingStrategyCards stats={stats} onToggle={toggle} />
      </Panel>
      <p className="text-xs text-terminal-muted">
        Stats are computed live from the current replay session. Start a replay from the HFT Terminal or here to
        populate signal counts and paper-trade performance. Unsafe/disabled strategies show a reject reason.
      </p>
    </div>
  );
}
