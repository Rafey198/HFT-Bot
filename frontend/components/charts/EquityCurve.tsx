"use client";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function EquityCurve({ data, height = 260 }: { data: { t: string; equity: number }[]; height?: number }) {
  if (!data?.length) return <Empty height={height} label="No equity data" />;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
        <defs>
          <linearGradient id="eq" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f5c451" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#f5c451" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="t" tick={false} axisLine={{ stroke: "#1c2435" }} />
        <YAxis tick={{ fill: "#8b97ad", fontSize: 10 }} axisLine={{ stroke: "#1c2435" }} width={56} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{ background: "#0f1524", border: "1px solid #1c2435", borderRadius: 6, fontSize: 12 }}
          labelStyle={{ color: "#8b97ad" }}
          formatter={(v: number) => [`$${Number(v).toFixed(2)}`, "Equity"]}
        />
        <Area type="monotone" dataKey="equity" stroke="#f5c451" strokeWidth={1.5} fill="url(#eq)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function DrawdownChart({ data, height = 200 }: { data: { t: string; drawdown: number }[]; height?: number }) {
  if (!data?.length) return <Empty height={height} label="No drawdown data" />;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
        <defs>
          <linearGradient id="dd" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ea3943" stopOpacity={0} />
            <stop offset="100%" stopColor="#ea3943" stopOpacity={0.45} />
          </linearGradient>
        </defs>
        <XAxis dataKey="t" tick={false} axisLine={{ stroke: "#1c2435" }} />
        <YAxis tick={{ fill: "#8b97ad", fontSize: 10 }} axisLine={{ stroke: "#1c2435" }} width={56} />
        <Tooltip
          contentStyle={{ background: "#0f1524", border: "1px solid #1c2435", borderRadius: 6, fontSize: 12 }}
          formatter={(v: number) => [`${Number(v).toFixed(2)}%`, "Drawdown"]}
        />
        <Area type="monotone" dataKey="drawdown" stroke="#ea3943" strokeWidth={1.2} fill="url(#dd)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function Empty({ height, label }: { height: number; label: string }) {
  return (
    <div className="flex items-center justify-center text-sm text-terminal-muted" style={{ height }}>
      {label}
    </div>
  );
}
