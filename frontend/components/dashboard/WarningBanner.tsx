import { AlertTriangle } from "lucide-react";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function WarningBanner({ children, tone = "warn" }: { children: ReactNode; tone?: "warn" | "danger" | "info" }) {
  const tones = {
    warn: "border-warn/40 bg-warn/10 text-warn",
    danger: "border-danger/50 bg-danger/10 text-danger",
    info: "border-gold/40 bg-gold/10 text-gold",
  };
  return (
    <div className={cn("flex items-start gap-2 rounded-md border px-3 py-2 text-xs", tones[tone])}>
      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
      <span className="leading-relaxed">{children}</span>
    </div>
  );
}
