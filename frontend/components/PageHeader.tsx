import { ReactNode } from "react";

export function PageHeader({ title, subtitle, right }: { title: string; subtitle?: string; right?: ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-gray-100">{title}</h1>
        {subtitle && <p className="mt-0.5 text-sm text-terminal-muted">{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}
