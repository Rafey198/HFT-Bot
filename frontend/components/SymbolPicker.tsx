"use client";

const SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"];
const TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"];

export function SymbolPicker({
  symbol,
  timeframe,
  onSymbol,
  onTimeframe,
  timeframes = TIMEFRAMES,
}: {
  symbol: string;
  timeframe: string;
  onSymbol: (s: string) => void;
  onTimeframe: (t: string) => void;
  timeframes?: string[];
}) {
  return (
    <div className="flex items-center gap-2">
      <select
        value={symbol}
        onChange={(e) => onSymbol(e.target.value)}
        className="rounded-md border border-terminal-border bg-terminal-panel px-2 py-1.5 text-xs text-gray-200 outline-none focus:border-gold/50"
      >
        {SYMBOLS.map((s) => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <select
        value={timeframe}
        onChange={(e) => onTimeframe(e.target.value)}
        className="rounded-md border border-terminal-border bg-terminal-panel px-2 py-1.5 text-xs text-gray-200 outline-none focus:border-gold/50"
      >
        {timeframes.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
    </div>
  );
}
