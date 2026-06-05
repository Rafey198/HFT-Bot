"use client";
import { cn } from "@/lib/utils";

export function MonthlyReturnsHeatmap({ data }: { data: { month: string; return: number }[] }) {
  if (!data?.length) return <div className="py-8 text-center text-sm text-terminal-muted">No monthly data</div>;

  const byYear: Record<string, Record<number, number>> = {};
  for (const d of data) {
    const [y, m] = d.month.split("-");
    byYear[y] = byYear[y] || {};
    byYear[y][parseInt(m, 10)] = d.return;
  }
  const years = Object.keys(byYear).sort();
  const months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];

  const color = (v: number | undefined) => {
    if (v === undefined) return "bg-terminal-panel/40 text-terminal-muted/40";
    const a = Math.min(1, Math.abs(v) / 8);
    if (v > 0) return `text-buy`;
    if (v < 0) return `text-sell`;
    return "text-terminal-muted";
  };
  const bg = (v: number | undefined) => {
    if (v === undefined) return "transparent";
    const a = Math.min(0.5, Math.abs(v) / 14 + 0.06);
    return v >= 0 ? `rgba(22,199,132,${a})` : `rgba(234,57,67,${a})`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-separate" style={{ borderSpacing: 2 }}>
        <thead>
          <tr>
            <th className="w-10" />
            {months.map((m, i) => (
              <th key={i} className="text-[10px] font-normal text-terminal-muted">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {years.map((y) => (
            <tr key={y}>
              <td className="mono text-[10px] text-terminal-muted">{y}</td>
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => {
                const v = byYear[y][m];
                return (
                  <td
                    key={m}
                    className={cn("mono rounded text-center text-[10px] leading-5", color(v))}
                    style={{ background: bg(v), minWidth: 26 }}
                    title={v !== undefined ? `${y}-${String(m).padStart(2, "0")}: ${v}%` : ""}
                  >
                    {v !== undefined ? v.toFixed(1) : ""}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
