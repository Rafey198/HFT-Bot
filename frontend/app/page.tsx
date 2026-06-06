"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Activity, ArrowRight, Database, Gauge, LineChart, Lock, Radar,
  ShieldCheck, TerminalSquare, Timer, Zap,
} from "lucide-react";
import { Disclaimer } from "@/components/dashboard/Disclaimer";
import { Button } from "@/components/ui/primitives";
import { api } from "@/lib/api";

const FEATURES = [
  { icon: Zap, title: "Fast market feed", desc: "Tick + simulated-tick streaming with live ticker, spread & latency meters." },
  { icon: Radar, title: "Signal scanner", desc: "10 fast scalping strategies scan every tick and expire quickly." },
  { icon: Gauge, title: "Execution queue", desc: "Latency, spread & slippage simulation with full order lifecycle." },
  { icon: ShieldCheck, title: "Strict risk control", desc: "Hard caps, kill switch, and a risk manager that overrides all signals." },
  { icon: LineChart, title: "Backtest + walk-forward", desc: "Realistic backtester with walk-forward validation to reduce overfitting." },
  { icon: Activity, title: "Regime detection", desc: "Trend/range/volatility regimes drive strategy selection." },
];

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const runDemo = async () => {
    setLoading(true);
    try {
      await api.replayStart({ symbol: "XAUUSD", timeframe: "M5", speed: 10, auto_execute: true });
      router.push("/hft-terminal");
    } catch {
      router.push("/hft-terminal");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-5">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="panel relative overflow-hidden p-8"
      >
        <div className="absolute right-0 top-0 h-48 w-48 rounded-full bg-gold/10 blur-3xl" />
        <div className="relative">
          <span className="chip border-gold/40 text-gold">XAUUSD · Forex · Research Simulator</span>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-gray-50 sm:text-4xl">
            AurumFX <span className="text-gold">HFT-Style</span> Quant Execution Agent
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-terminal-muted">
            HFT-style retail quant execution, backtesting, tick replay, paper trading, and risk-control
            terminal for XAUUSD/Forex. This mimics the workflow of fast execution systems using tick replay,
            rapid signal scanning, execution queues, latency monitoring, and strict risk controls.
            It is <span className="text-gray-200">not institutional HFT</span> and does not guarantee profit.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Button variant="gold" onClick={runDemo} disabled={loading}>
              <Zap size={15} /> {loading ? "Starting…" : "Run Demo Replay"}
            </Button>
            <Link href="/hft-terminal"><Button><TerminalSquare size={15} /> Open HFT Terminal</Button></Link>
            <Link href="/data-center"><Button variant="ghost"><Database size={15} /> Upload Data</Button></Link>
          </div>
        </div>
      </motion.div>

      <Disclaimer />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f, i) => {
          const Icon = f.icon;
          return (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="panel p-4"
            >
              <Icon size={18} className="text-gold" />
              <h3 className="mt-2 text-sm font-semibold text-gray-100">{f.title}</h3>
              <p className="mt-1 text-xs leading-relaxed text-terminal-muted">{f.desc}</p>
            </motion.div>
          );
        })}
      </div>

      <div className="panel p-5">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-terminal-muted">Architecture preview</h2>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {["Data Ingestion", "Feature Engineering", "35 Strategies", "Backtest", "Walk-Forward", "Regime", "Signal Scanner", "Spread Guard", "Risk Manager", "Execution Queue", "Paper Broker", "Journal"].map((n, i, arr) => (
            <div key={n} className="flex items-center gap-2">
              <span className="rounded-md border border-terminal-border bg-terminal-panel px-2.5 py-1 text-gray-300">{n}</span>
              {i < arr.length - 1 && <ArrowRight size={12} className="text-terminal-muted" />}
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/tick-replay"><Button size="sm"><Timer size={13} /> Tick Replay</Button></Link>
          <Link href="/paper-trading"><Button size="sm"><Activity size={13} /> Paper Trading</Button></Link>
          <Link href="/live-execution"><Button size="sm" variant="ghost"><Lock size={13} /> Live Execution (locked)</Button></Link>
        </div>
      </div>
    </div>
  );
}
