"use client";
import { useEffect, useRef } from "react";
import { cn, timeShort } from "@/lib/utils";

interface LogEntry {
  ts: string;
  level: string;
  message: string;
}

const LEVEL_COLORS: Record<string, string> = {
  open: "text-buy",
  close: "text-gold",
  blocked: "text-warn",
  kill: "text-danger",
  system: "text-terminal-muted",
  info: "text-gray-300",
};

export function ExecutionLog({ logs }: { logs: LogEntry[] }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = 0;
  }, [logs]);

  return (
    <div ref={ref} className="h-full space-y-0.5 overflow-y-auto font-mono text-[11px] leading-relaxed">
      {logs.map((l, i) => (
        <div key={i} className="flex gap-2">
          <span className="shrink-0 text-terminal-muted/60">{timeShort(l.ts)}</span>
          <span className={cn("shrink-0 uppercase", LEVEL_COLORS[l.level] || "text-gray-400")}>[{l.level}]</span>
          <span className="text-gray-300">{l.message}</span>
        </div>
      ))}
      {!logs.length && <div className="py-6 text-center text-xs text-terminal-muted">Execution log empty.</div>}
    </div>
  );
}
