export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function fmt(n: number | undefined | null, digits = 2): string {
  if (n === undefined || n === null || Number.isNaN(n)) return "—";
  return n.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function fmtPrice(n: number | undefined | null, digits = 5): string {
  if (n === undefined || n === null || Number.isNaN(n)) return "—";
  return n.toFixed(digits);
}

export function fmtMoney(n: number | undefined | null): string {
  if (n === undefined || n === null || Number.isNaN(n)) return "—";
  return `$${n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function pctColor(v: number): string {
  if (v > 0) return "text-buy";
  if (v < 0) return "text-sell";
  return "text-terminal-muted";
}

export function timeShort(ts: string): string {
  if (!ts) return "—";
  try {
    return new Date(ts).toLocaleTimeString("en-GB", { hour12: false });
  } catch {
    return ts.slice(11, 19);
  }
}

export const DISCLAIMER =
  "This system is for research, backtesting, and educational purposes. Forex and gold trading are high risk. Past performance does not guarantee future results. This system can lose money. Always use paper trading before live execution.";

export const RECO_COLORS: Record<string, string> = {
  candidate: "text-buy border-buy/40 bg-buy/10",
  paper_test: "text-warn border-warn/40 bg-warn/10",
  reject: "text-sell border-sell/40 bg-sell/10",
};
