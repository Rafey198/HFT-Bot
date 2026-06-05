export interface Tick {
  timestamp: string;
  symbol: string;
  bid: number;
  ask: number;
  mid: number;
  spread: number;
  volume: number;
  source: string;
}

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface TradeMarker {
  time: string;
  price: number;
  side: string;
  type?: string;
  pnl?: number;
}

export interface HftSignal {
  signal_id: string;
  timestamp: string;
  symbol: string;
  side: "buy" | "sell" | "hold";
  confidence: number;
  strategy: string;
  strategy_key?: string;
  entry: number;
  stop_loss: number;
  take_profit: number;
  valid_for_ms: number;
  reason: string;
  blocked_reason: string;
}

export interface OrderState {
  order_id: string;
  signal_id: string;
  strategy: string;
  symbol: string;
  side: string;
  lot_size: number;
  requested_price: number;
  filled_price: number;
  latency_ms: number;
  slippage: number;
  state: string;
  reason: string;
  ts: string;
}

export interface Position {
  trade_id: string;
  symbol: string;
  side: string;
  entry_time: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  exit_time: string;
  exit_price: number;
  lot_size: number;
  pnl: number;
  pnl_percent: number;
  status: string;
  strategy: string;
  reason: string;
}

export interface RiskState {
  balance: number;
  equity: number;
  daily_pnl: number;
  daily_pnl_percent: number;
  weekly_pnl: number;
  drawdown_percent: number;
  max_daily_loss: number;
  max_drawdown_stop: number;
  consecutive_losses: number;
  open_positions: number;
  trades_today: number;
  trades_per_minute: number;
  max_trades_per_minute: number;
  kill_switch_active: boolean;
  kill_reason: string;
  auto_disabled: boolean;
  risk_status: "safe" | "warning" | "blocked";
}

export interface Latency {
  market_feed_latency_ms: number;
  signal_latency_ms: number;
  risk_latency_ms: number;
  execution_latency_ms: number;
  broker_latency_ms: number;
  total_latency_ms: number;
  status: "excellent" | "acceptable" | "slow" | "dangerous";
}

export interface ReplayState {
  running: boolean;
  paused: boolean;
  speed: number;
  symbol: string;
  timeframe: string;
  cursor: number;
  total: number;
  clock: string;
  auto_execute: boolean;
  source: string;
  progress: number;
}

export interface StrategyInfo {
  name: string;
  key: string;
  category: string;
  description: string;
  parameters: Record<string, unknown>;
  enabled: boolean;
}

export interface BacktestResult {
  strategy_name: string;
  strategy_key?: string;
  symbol: string;
  timeframe: string;
  total_return: number;
  cagr: number;
  win_rate: number;
  profit_factor: number;
  expectancy: number;
  max_drawdown: number;
  sharpe: number;
  sortino: number;
  calmar: number;
  avg_win: number;
  avg_loss: number;
  avg_hold_time: number;
  risk_reward: number;
  longest_losing_streak: number;
  num_trades: number;
  exposure_time: number;
  recommendation: string;
  warnings: string[];
  equity_curve: { t: string; equity: number }[];
  drawdown_curve: { t: string; drawdown: number }[];
  monthly_returns: { month: string; return: number }[];
  yearly_returns: { year: string; return: number }[];
  trades: Position[];
  safety?: { warnings: string[]; must_fix_before_live: string[] };
}

export interface DataReport {
  symbol: string;
  timeframe: string;
  rows: number;
  start_date: string;
  end_date: string;
  missing_candles: number;
  duplicate_rows_removed: number;
  invalid_rows_removed: number;
  data_quality_score: number;
  warnings: string[];
  kind: string;
  dataset_id: string;
}
