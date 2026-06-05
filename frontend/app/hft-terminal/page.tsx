"use client";
import { useCallback } from "react";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/usePoll";
import {
  HftSignal, Latency, OrderState, Position, ReplayState, RiskState, Tick, TradeMarker, Candle,
} from "@/lib/types";
import { Panel } from "@/components/ui/primitives";
import { HftTerminalLayout } from "@/components/hft/HftTerminalLayout";
import { HftStatusBar } from "@/components/hft/HftStatusBar";
import { LivePriceTicker } from "@/components/hft/LivePriceTicker";
import { BidAskPanel } from "@/components/hft/BidAskPanel";
import { SpreadMeter } from "@/components/hft/SpreadMeter";
import { LatencyMeter } from "@/components/hft/LatencyMeter";
import { SignalScannerFeed } from "@/components/hft/SignalScannerFeed";
import { ExecutionQueuePanel } from "@/components/hft/ExecutionQueuePanel";
import { OrderFlowPanel } from "@/components/hft/OrderFlowPanel";
import { OpenPositionsPanel } from "@/components/hft/OpenPositionsPanel";
import { ClosedTradesPanel } from "@/components/hft/ClosedTradesPanel";
import { RiskKillSwitch } from "@/components/hft/RiskKillSwitch";
import { ReplayControls } from "@/components/hft/ReplayControls";
import { ExecutionLog } from "@/components/hft/ExecutionLog";
import { CandlestickChart } from "@/components/charts/CandlestickChart";
import { Disclaimer } from "@/components/dashboard/Disclaimer";

interface MarketEvent {
  tick: Tick;
  candles: Candle[];
  markers: TradeMarker[];
  regime: { regime: string; confidence: number };
  state: ReplayState;
}

export default function HftTerminalPage() {
  const { data: market } = usePoll<MarketEvent>(() => api.marketEvent() as Promise<MarketEvent>, 700);
  const { data: signalsRes } = usePoll<{ signals: HftSignal[] }>(() => api.hftSignals(), 800);
  const { data: queueRes } = usePoll<{ orders: OrderState[] }>(() => api.executionQueue(), 900);
  const { data: latency } = usePoll<Latency>(() => api.latency() as Promise<Latency>, 1200);
  const { data: risk } = usePoll<RiskState>(() => api.riskState() as Promise<RiskState>, 1000);
  const { data: logsRes } = usePoll<{ logs: any[] }>(() => api.hftLogs(), 900);
  const { data: paper } = usePoll<any>(() => api.paperState(), 1500);

  const state = market?.state;
  const onStart = useCallback(() => api.replayStart({ symbol: "XAUUSD", timeframe: "M5", speed: state?.speed || 10, auto_execute: true }), [state?.speed]);
  const onKill = useCallback((a: boolean) => api.killSwitch({ activate: a, reason: a ? "Manual kill switch (terminal)" : "" }), []);
  const onClosePos = useCallback((id: string) => api.closeOrder({ trade_id: id }), []);

  const orders = queueRes?.orders || [];
  const positions: Position[] = paper?.broker?.open_positions || [];
  const closed: Position[] = paper?.broker?.closed_trades || [];

  return (
    <HftTerminalLayout
      statusBar={
        <div className="space-y-2">
          <HftStatusBar tick={market?.tick} latency={latency || undefined} risk={risk || undefined} state={state} />
          <div className="flex flex-wrap items-center justify-between gap-2">
            <ReplayControls
              state={state}
              onStart={onStart}
              onPause={() => api.replayPause()}
              onResume={() => api.replayResume()}
              onReset={() => api.replayReset()}
              onSpeed={(s) => api.replaySpeed(s)}
            />
            {market?.regime && (
              <span className="chip border-gold/30 text-gold">
                Regime: {market.regime.regime.replace(/_/g, " ")} · {market.regime.confidence}%
              </span>
            )}
          </div>
        </div>
      }
      left={
        <>
          <Panel title="Market Feed">
            <div className="space-y-2">
              <LivePriceTicker tick={market?.tick} />
              <BidAskPanel tick={market?.tick} />
              <SpreadMeter tick={market?.tick} maxSpreadPoints={30} />
              <LatencyMeter latency={latency || undefined} />
            </div>
          </Panel>
          <Panel title="Risk & Kill Switch">
            <div className="space-y-2">
              <RiskKillSwitch risk={risk || undefined} onToggle={onKill} />
              {risk && (
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <MiniStat label="Day P/L" value={`${risk.daily_pnl_percent}%`} tone={risk.daily_pnl >= 0 ? "text-buy" : "text-sell"} />
                  <MiniStat label="Drawdown" value={`${risk.drawdown_percent}%`} tone="text-warn" />
                  <MiniStat label="Streak" value={`${risk.consecutive_losses}`} tone="text-gray-200" />
                  <MiniStat label="Trades/min" value={`${risk.trades_per_minute}/${risk.max_trades_per_minute}`} tone="text-gray-200" />
                </div>
              )}
            </div>
          </Panel>
        </>
      }
      center={
        <>
          <Panel title={`Live Chart — ${state?.symbol || "XAUUSD"} ${state?.timeframe || ""}`} bodyClassName="p-1">
            <CandlestickChart candles={market?.candles || []} markers={market?.markers || []} height={340} />
          </Panel>
          <Panel title="Order Flow">
            <OrderFlowPanel orders={orders} />
          </Panel>
          <Panel title="Execution Log">
            <div className="h-40">
              <ExecutionLog logs={logsRes?.logs || []} />
            </div>
          </Panel>
        </>
      }
      right={
        <>
          <Panel title="Signal Scanner">
            <SignalScannerFeed signals={signalsRes?.signals || []} />
          </Panel>
        </>
      }
      bottom={
        <>
          <Panel title="Execution Queue" className="lg:col-span-5">
            <ExecutionQueuePanel orders={orders} />
          </Panel>
          <Panel title={`Open Positions (${positions.length})`} className="lg:col-span-3">
            <OpenPositionsPanel positions={positions} onClose={onClosePos} />
          </Panel>
          <Panel title={`Closed Trades (${closed.length})`} className="lg:col-span-4">
            <ClosedTradesPanel trades={closed} />
          </Panel>
          <div className="lg:col-span-12">
            <Disclaimer compact />
          </div>
        </>
      }
    />
  );
}

function MiniStat({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="rounded-md border border-terminal-border bg-terminal-panel/40 px-2 py-1.5">
      <div className="text-[9px] uppercase text-terminal-muted">{label}</div>
      <div className={`mono text-sm font-semibold ${tone}`}>{value}</div>
    </div>
  );
}
