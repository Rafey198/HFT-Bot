import { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function MetricCard({
  label,
  value,
  sub,
  tone,
  icon,
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  tone?: "buy" | "sell" | "gold" | "default";
  icon?: ReactNode;
}) {
  const toneClass = {
    buy: "text-buy",
    sell: "text-sell",
    gold: "text-gold",
    default: "text-gray-100",
  }[tone || "default"];
  return (
    <div className="panel p-3">
      <div className="flex items-center justify-between text-[11px] uppercase tracking-wider text-terminal-muted">
        <span>{label}</span>
        {icon}
      </div>
      <div className={cn("mono mt-1 text-xl font-semibold", toneClass)}>{value}</div>
      {sub && <div className="mt-0.5 text-xs text-terminal-muted">{sub}</div>}
    </div>
  );
}
