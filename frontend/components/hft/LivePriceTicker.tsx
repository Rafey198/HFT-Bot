"use client";
import { useEffect, useRef, useState } from "react";
import { Tick } from "@/lib/types";
import { cn } from "@/lib/utils";

export function LivePriceTicker({ tick }: { tick?: Tick }) {
  const [flash, setFlash] = useState<"up" | "down" | null>(null);
  const prev = useRef<number | undefined>(undefined);

  useEffect(() => {
    if (!tick) return;
    if (prev.current !== undefined && tick.mid !== prev.current) {
      setFlash(tick.mid > prev.current ? "up" : "down");
      const id = setTimeout(() => setFlash(null), 500);
      prev.current = tick.mid;
      return () => clearTimeout(id);
    }
    prev.current = tick.mid;
  }, [tick?.mid]);

  return (
    <div
      className={cn(
        "rounded-md border border-terminal-border px-3 py-2 transition-colors",
        flash === "up" && "animate-flashGreen",
        flash === "down" && "animate-flashRed",
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-gold">
          {tick?.symbol || "XAUUSD"}
        </span>
        <span className="text-[10px] text-terminal-muted">{tick?.source || "—"}</span>
      </div>
      <div
        className={cn(
          "mono mt-1 text-3xl font-bold transition-colors",
          flash === "up" ? "text-buy" : flash === "down" ? "text-sell" : "text-gray-100",
        )}
      >
        {tick ? tick.mid.toFixed(tick.mid > 50 ? 2 : 5) : "—"}
      </div>
    </div>
  );
}
