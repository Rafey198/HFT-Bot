"use client";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Panel({
  title,
  right,
  children,
  className,
  bodyClassName,
}: {
  title?: ReactNode;
  right?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <div className={cn("panel flex flex-col", className)}>
      {title && (
        <div className="panel-header">
          <span>{title}</span>
          {right}
        </div>
      )}
      <div className={cn("flex-1 overflow-auto p-3", bodyClassName)}>{children}</div>
    </div>
  );
}

export function Button({
  children,
  onClick,
  variant = "default",
  size = "md",
  disabled,
  className,
  type = "button",
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "default" | "gold" | "buy" | "sell" | "ghost" | "danger";
  size?: "sm" | "md";
  disabled?: boolean;
  className?: string;
  type?: "button" | "submit";
}) {
  const variants: Record<string, string> = {
    default: "bg-terminal-panel border-terminal-border hover:border-gold/50 text-gray-200",
    gold: "bg-gold/15 border-gold/50 text-gold hover:bg-gold/25",
    buy: "bg-buy/15 border-buy/50 text-buy hover:bg-buy/25",
    sell: "bg-sell/15 border-sell/50 text-sell hover:bg-sell/25",
    danger: "bg-danger/20 border-danger text-white hover:bg-danger/40",
    ghost: "bg-transparent border-transparent hover:bg-terminal-panel text-terminal-muted",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center gap-1.5 rounded-md border font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-40",
        size === "sm" ? "px-2.5 py-1 text-xs" : "px-3.5 py-2 text-sm",
        variants[variant],
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Badge({
  children,
  className,
  tone = "default",
}: {
  children: ReactNode;
  className?: string;
  tone?: "default" | "buy" | "sell" | "warn" | "gold" | "muted";
}) {
  const tones: Record<string, string> = {
    default: "border-terminal-border text-gray-300",
    buy: "border-buy/40 text-buy bg-buy/10",
    sell: "border-sell/40 text-sell bg-sell/10",
    warn: "border-warn/40 text-warn bg-warn/10",
    gold: "border-gold/40 text-gold bg-gold/10",
    muted: "border-terminal-border text-terminal-muted",
  };
  return <span className={cn("chip", tones[tone], className)}>{children}</span>;
}

export function Spinner() {
  return (
    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gold/30 border-t-gold" />
  );
}
