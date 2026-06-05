"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity, BarChart3, Database, Gauge, LineChart, Radar,
  ScrollText, Settings, ShieldAlert, Siren, Sparkles, TerminalSquare,
  Timer, TrendingUp, Wallet, Lock, FlaskConical,
} from "lucide-react";
import { cn } from "@/lib/utils";

const Flask = FlaskConical || Sparkles;

const NAV = [
  { group: "Overview", items: [{ href: "/", label: "Home", icon: TrendingUp }] },
  {
    group: "Research",
    items: [
      { href: "/data-center", label: "Data Center", icon: Database },
      { href: "/strategy-lab", label: "Strategy Lab", icon: Flask },
      { href: "/backtest", label: "Backtest", icon: BarChart3 },
      { href: "/walk-forward", label: "Walk-Forward", icon: LineChart },
      { href: "/regime-monitor", label: "Regime Monitor", icon: Radar },
    ],
  },
  {
    group: "Execution",
    items: [
      { href: "/hft-terminal", label: "HFT Terminal", icon: TerminalSquare },
      { href: "/tick-replay", label: "Tick Replay", icon: Timer },
      { href: "/scalping-lab", label: "Scalping Lab", icon: Activity },
      { href: "/execution-monitor", label: "Execution Monitor", icon: Gauge },
      { href: "/paper-trading", label: "Paper Trading", icon: Wallet },
      { href: "/live-execution", label: "Live Execution", icon: Lock },
    ],
  },
  {
    group: "Control",
    items: [
      { href: "/risk-kill-center", label: "Risk Kill Center", icon: Siren },
      { href: "/journal", label: "Journal", icon: ScrollText },
      { href: "/explainability", label: "Explainability", icon: ShieldAlert },
      { href: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-terminal-border bg-terminal-panel/60 md:flex">
      <div className="flex items-center gap-2 border-b border-terminal-border px-4 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gold/15 text-gold shadow-glow">
          <span className="mono text-sm font-bold">Au</span>
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight text-gold">AurumFX</div>
          <div className="text-[10px] uppercase tracking-widest text-terminal-muted">HFT-Style Quant</div>
        </div>
      </div>
      <nav className="flex-1 space-y-4 overflow-y-auto px-2 py-4">
        {NAV.map((section) => (
          <div key={section.group}>
            <div className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-widest text-terminal-muted/60">
              {section.group}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 rounded-md px-3 py-1.5 text-sm transition-colors",
                    active
                      ? "bg-gold/10 text-gold"
                      : "text-gray-400 hover:bg-terminal-card hover:text-gray-100",
                  )}
                >
                  <Icon size={15} className={active ? "text-gold" : ""} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="border-t border-terminal-border px-3 py-3 text-[10px] leading-relaxed text-terminal-muted/70">
        Live trading disabled by default. Research & paper only.
      </div>
    </aside>
  );
}
