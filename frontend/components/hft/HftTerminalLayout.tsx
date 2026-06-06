"use client";
import { ReactNode } from "react";

export function HftTerminalLayout({
  statusBar,
  left,
  center,
  right,
  bottom,
}: {
  statusBar: ReactNode;
  left: ReactNode;
  center: ReactNode;
  right: ReactNode;
  bottom: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 p-3">
      {statusBar}
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-12">
        <div className="space-y-3 lg:col-span-3">{left}</div>
        <div className="space-y-3 lg:col-span-6">{center}</div>
        <div className="space-y-3 lg:col-span-3">{right}</div>
      </div>
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-12">{bottom}</div>
    </div>
  );
}
