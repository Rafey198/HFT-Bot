import { ShieldAlert } from "lucide-react";
import { DISCLAIMER } from "@/lib/utils";

export function Disclaimer({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-start gap-2 rounded-md border border-warn/40 bg-warn/5 px-3 py-2 text-warn">
      <ShieldAlert size={compact ? 14 : 16} className="mt-0.5 shrink-0" />
      <p className={compact ? "text-[11px] leading-relaxed" : "text-xs leading-relaxed"}>{DISCLAIMER}</p>
    </div>
  );
}
