import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "AurumFX — HFT-Style Quant Execution Agent",
  description:
    "HFT-style retail quant execution, backtesting, tick replay, paper trading, and risk-control terminal for XAUUSD/Forex. Research only.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
