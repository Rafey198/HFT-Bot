"use client";
import { useCallback, useRef, useState } from "react";
import { Upload } from "lucide-react";
import { api, API_BASE } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import { Candle, ReplayState, Tick, TradeMarker, Position } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Panel, Button } from "@/components/ui/primitives";
import { SymbolPicker } from "@/components/SymbolPicker";
import { ReplayControls } from "@/components/hft/ReplayControls";
import { LivePriceTicker } from "@/components/hft/LivePriceTicker";
import { CandlestickChart } from "@/components/charts/CandlestickChart";
import { ClosedTradesPanel } from "@/components/hft/ClosedTradesPanel";
import { Disclaimer } from "@/components/dashboard/Disclaimer";

interface MarketEvent { tick: Tick; candles: Candle[]; markers: TradeMarker[]; state: ReplayState; }

export default function TickReplayPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("M5");
  const [auto, setAuto] = useState(true);
  const fileRef = useRef<HTMLInputElement>(null);
  const { data: market } = usePoll<MarketEvent>(() => api.marketEvent() as Promise<MarketEvent>, 700);
  const { data: paper } = usePoll<any>(() => api.paperState(), 1500);
  const state = market?.state;

  const onStart = useCallback(() => api.replayStart({ symbol, timeframe, speed: state?.speed || 10, auto_execute: auto }), [symbol, timeframe, state?.speed, auto]);
  const onUpload = async (file: File) => {
    const r: any = await api.uploadCsv(file, symbol, "");
    await api.replayStart({ dataset_id: r.dataset_id, symbol, timeframe, speed: 10, auto_execute: auto });
  };
  const closed: Position[] = paper?.broker?.closed_trades || [];

  return (
    <div className="space-y-4 p-5">
      <PageHeader
        title="Tick Replay"
        subtitle="Replay tick or OHLCV data at 1x–100x with live paper execution."
        right={<SymbolPicker symbol={symbol} timeframe={timeframe} onSymbol={setSymbol} onTimeframe={setTimeframe} />}
      />
      <Disclaimer compact />

      <Panel title="Replay Controls">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <ReplayControls
            state={state}
            onStart={onStart}
            onPause={() => api.replayPause()}
            onResume={() => api.replayResume()}
            onReset={() => api.replayReset()}
            onSpeed={(s) => api.replaySpeed(s)}
          />
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1.5 text-xs text-terminal-muted">
              <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} /> Paper execute
            </label>
            <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])} />
            <Button onClick={() => fileRef.current?.click()}><Upload size={14} /> Upload CSV</Button>
            <a href={`${API_BASE}/api/journal/export?fmt=csv`} target="_blank" rel="noreferrer">
              <Button variant="ghost">Export Replay Trades</Button>
            </a>
          </div>
        </div>
      </Panel>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="space-y-3 lg:col-span-1">
          <LivePriceTicker tick={market?.tick} />
          <Panel title="Replay Clock">
            <div className="mono text-center text-lg text-gold">{state?.clock?.slice(11, 19) || "--:--:--"}</div>
            <div className="mt-2 text-center text-xs text-terminal-muted">{state?.cursor || 0} / {state?.total || 0} ticks</div>
            <div className="mt-1 text-center text-xs text-terminal-muted">{state?.source}</div>
          </Panel>
        </div>
        <Panel title="Stream Chart" className="lg:col-span-3" bodyClassName="p-1">
          <CandlestickChart candles={market?.candles || []} markers={market?.markers || []} height={360} />
        </Panel>
      </div>

      <Panel title={`Replay Paper Trades (${closed.length})`}>
        <ClosedTradesPanel trades={closed} />
      </Panel>
    </div>
  );
}
