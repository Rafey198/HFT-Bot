// In Cursor online / forwarded previews the browser cannot reach the VM's
// 127.0.0.1:8000 directly, so we default to a SAME-ORIGIN proxy path ("/backend")
// which Next.js rewrites to the backend server-side (see next.config.mjs).
// Override with NEXT_PUBLIC_API_URL or NEXT_PUBLIC_API_BASE for local/direct setups.
const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "/backend";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    cache: "no-store",
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  base: API_BASE,
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),

  // Data
  symbols: () => request<{ symbols: string[]; primary: string; timeframes: string[] }>("/api/data/symbols"),
  generateDemo: (body: { symbol: string; timeframe: string; years: number; kind?: string }) =>
    request("/api/data/generate-demo", { method: "POST", body: JSON.stringify(body) }),
  datasets: () => request<{ datasets: any[] }>("/api/data/list"),
  dataSummary: (id: string) => request(`/api/data/summary?dataset_id=${id}`),

  uploadCsv: async (file: File, symbol: string, timeframe: string) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("symbol", symbol);
    fd.append("timeframe", timeframe);
    const res = await fetch(`${API_BASE}/api/data/upload`, { method: "POST", body: fd });
    if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
    return res.json();
  },

  // Strategies / backtest
  strategies: () => request<{ count: number; strategies: any[]; categories: Record<string, string[]> }>("/api/strategies/list"),
  runStrategy: (body: any) => request("/api/strategies/run", { method: "POST", body: JSON.stringify(body) }),
  backtest: (body: any) => request("/api/backtest/run", { method: "POST", body: JSON.stringify(body) }),
  backtestAll: (body: any) => request("/api/backtest/run-all", { method: "POST", body: JSON.stringify(body) }),
  walkForward: (body: any) => request("/api/walk-forward/run", { method: "POST", body: JSON.stringify(body) }),
  regime: (body: any) => request("/api/regime/detect", { method: "POST", body: JSON.stringify(body) }),

  // HFT
  replayStart: (body: any) => request("/api/hft/replay/start", { method: "POST", body: JSON.stringify(body) }),
  replayPause: () => request("/api/hft/replay/pause", { method: "POST" }),
  replayResume: () => request("/api/hft/replay/resume", { method: "POST" }),
  replayReset: () => request("/api/hft/replay/reset", { method: "POST" }),
  replaySpeed: (speed: number) => request(`/api/hft/replay/speed?speed=${speed}`, { method: "POST" }),
  marketEvent: () => request("/api/hft/market-event"),
  hftSignals: () => request<{ signals: any[] }>("/api/hft/signals"),
  executionQueue: () => request<{ orders: any[] }>("/api/hft/execution-queue"),
  latency: () => request("/api/hft/latency"),
  riskState: () => request("/api/hft/risk-state"),
  hftLogs: () => request<{ logs: any[] }>("/api/hft/logs"),
  scalpingStats: () => request("/api/hft/scalping-stats"),
  explain: () => request("/api/hft/explain"),

  // Paper
  paperStart: (body: any) => request("/api/paper/start", { method: "POST", body: JSON.stringify(body) }),
  paperStop: () => request("/api/paper/stop", { method: "POST" }),
  paperState: () => request("/api/paper/state"),

  // Execution
  manualOrder: (body: any) => request("/api/execution/order", { method: "POST", body: JSON.stringify(body) }),
  closeOrder: (body: any) => request("/api/execution/close", { method: "POST", body: JSON.stringify(body) }),
  killSwitch: (body: any) => request("/api/execution/kill-switch", { method: "POST", body: JSON.stringify(body) }),

  // Risk
  riskSettings: () => request("/api/risk/settings"),
  updateRiskSettings: (body: any) => request("/api/risk/settings", { method: "POST", body: JSON.stringify(body) }),
  liveCheck: (body: any) => request("/api/risk/live-check", { method: "POST", body: JSON.stringify(body) }),
  safety: (body: any) => request("/api/risk/safety", { method: "POST", body: JSON.stringify(body) }),

  // Journal / reports
  journal: (query = "") => request(`/api/journal/trades${query}`),
  reportBacktest: (key = "") => request(`/api/report/backtest?strategy_key=${key}`),
  reportPaper: () => request("/api/report/paper"),
};

export { API_BASE };
