"use client";
import { motion, AnimatePresence } from "framer-motion";
import { HftSignal } from "@/lib/types";
import { cn, timeShort } from "@/lib/utils";

export function SignalScannerFeed({ signals }: { signals: HftSignal[] }) {
  return (
    <div className="space-y-1.5">
      <AnimatePresence initial={false}>
        {signals.slice(0, 18).map((s) => {
          const buy = s.side === "buy";
          const blocked = !!s.blocked_reason;
          return (
            <motion.div
              key={s.signal_id}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              className={cn(
                "rounded-md border px-2.5 py-1.5 text-xs",
                blocked
                  ? "border-terminal-border bg-terminal-panel/40 opacity-70"
                  : buy
                  ? "border-buy/30 bg-buy/5"
                  : "border-sell/30 bg-sell/5",
              )}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <span className={cn("h-1.5 w-1.5 rounded-full", buy ? "bg-buy animate-pulseDot" : "bg-sell animate-pulseDot")} />
                  <span className="font-semibold text-gray-200">{s.strategy}</span>
                </span>
                <span className={cn("mono font-bold uppercase", buy ? "text-buy" : "text-sell")}>{s.side}</span>
              </div>
              <div className="mt-0.5 flex items-center justify-between text-[10px] text-terminal-muted">
                <span className="mono">@ {s.entry.toFixed(2)} · conf {s.confidence}</span>
                <span>{timeShort(s.timestamp)}</span>
              </div>
              {blocked && <div className="mt-0.5 text-[10px] text-warn">blocked: {s.blocked_reason}</div>}
            </motion.div>
          );
        })}
      </AnimatePresence>
      {!signals.length && <div className="py-6 text-center text-xs text-terminal-muted">Scanning for signals…</div>}
    </div>
  );
}
