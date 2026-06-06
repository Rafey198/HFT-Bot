"use client";
import { useMemo } from "react";
import { Candle, TradeMarker } from "@/lib/types";

interface Props {
  candles: Candle[];
  markers?: TradeMarker[];
  height?: number;
  accent?: string;
}

export function CandlestickChart({ candles, markers = [], height = 360, accent = "#f5c451" }: Props) {
  const W = 900;
  const H = height;
  const padL = 8;
  const padR = 62;
  const padTB = 14;

  const { bars, scaleY, min, max, cw } = useMemo(() => {
    if (!candles.length) return { bars: [], scaleY: (v: number) => 0, min: 0, max: 1, cw: 1 };
    const lows = candles.map((c) => c.low);
    const highs = candles.map((c) => c.high);
    const mn = Math.min(...lows);
    const mx = Math.max(...highs);
    const range = mx - mn || 1;
    const innerH = H - padTB * 2;
    const innerW = W - padL - padR;
    const cwidth = innerW / candles.length;
    const sY = (v: number) => padTB + (mx - v) / range * innerH;
    const sX = (i: number) => padL + i * cwidth + cwidth / 2;
    const bars = candles.map((c, i) => ({
      x: sX(i),
      openY: sY(c.open),
      closeY: sY(c.close),
      highY: sY(c.high),
      lowY: sY(c.low),
      up: c.close >= c.open,
    }));
    return { bars, scaleY: sY, min: mn, max: mx, cw: cwidth };
  }, [candles, H]);

  if (!candles.length) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-terminal-muted" style={{ height }}>
        No price data yet — start a replay.
      </div>
    );
  }

  const bodyW = Math.max(1.5, cw * 0.6);
  const lastClose = candles[candles.length - 1].close;
  const ticks = 5;
  const gridLines = Array.from({ length: ticks + 1 }, (_, i) => {
    const v = min + (max - min) * (i / ticks);
    return { v, y: scaleY(v) };
  });

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height }} preserveAspectRatio="none">
      {gridLines.map((g, i) => (
        <g key={i}>
          <line x1={padL} x2={W - padR} y1={g.y} y2={g.y} stroke="#1c2435" strokeWidth={0.5} />
          <text x={W - padR + 4} y={g.y + 3} fill="#8b97ad" fontSize={9} className="mono">
            {g.v.toFixed(2)}
          </text>
        </g>
      ))}
      {bars.map((b, i) => (
        <g key={i}>
          <line x1={b.x} x2={b.x} y1={b.highY} y2={b.lowY} stroke={b.up ? "#16c784" : "#ea3943"} strokeWidth={0.8} />
          <rect
            x={b.x - bodyW / 2}
            y={Math.min(b.openY, b.closeY)}
            width={bodyW}
            height={Math.max(1, Math.abs(b.closeY - b.openY))}
            fill={b.up ? "#16c784" : "#ea3943"}
          />
        </g>
      ))}
      {/* last price line */}
      <line x1={padL} x2={W - padR} y1={scaleY(lastClose)} y2={scaleY(lastClose)} stroke={accent} strokeWidth={0.6} strokeDasharray="3 3" />
      <rect x={W - padR} y={scaleY(lastClose) - 7} width={padR} height={14} fill={accent} />
      <text x={W - padR + 3} y={scaleY(lastClose) + 3} fill="#05070d" fontSize={9} fontWeight="bold" className="mono">
        {lastClose.toFixed(2)}
      </text>
      {/* trade markers */}
      {markers.slice(0, 40).map((m, i) => {
        if (!m.price || m.price < min || m.price > max) return null;
        const y = scaleY(m.price);
        const x = W - padR - 6 - (i % 30) * 0;
        const color = m.type === "close" ? accent : m.side === "buy" ? "#16c784" : "#ea3943";
        return (
          <g key={i}>
            <circle cx={W - padR - 10} cy={y} r={2.4} fill={color} />
          </g>
        );
      })}
    </svg>
  );
}
