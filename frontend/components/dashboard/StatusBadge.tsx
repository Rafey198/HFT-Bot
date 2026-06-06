import { cn } from "@/lib/utils";

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    excellent: "text-buy border-buy/40 bg-buy/10",
    acceptable: "text-gold border-gold/40 bg-gold/10",
    safe: "text-buy border-buy/40 bg-buy/10",
    warning: "text-warn border-warn/40 bg-warn/10",
    slow: "text-warn border-warn/40 bg-warn/10",
    blocked: "text-danger border-danger/40 bg-danger/10",
    dangerous: "text-danger border-danger/40 bg-danger/10",
    candidate: "text-buy border-buy/40 bg-buy/10",
    paper_test: "text-warn border-warn/40 bg-warn/10",
    reject: "text-sell border-sell/40 bg-sell/10",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
        map[status] || "text-terminal-muted border-terminal-border",
      )}
    >
      <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-current" />
      {status.replace(/_/g, " ")}
    </span>
  );
}
