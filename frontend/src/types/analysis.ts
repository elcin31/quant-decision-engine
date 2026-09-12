/** TypeScript contracts mirroring FastAPI / Pydantic models. */

export type AnalysisMethod =
  | "returns"
  | "volatility"
  | "drawdown"
  | "var"
  | "cvar"
  | "risk"
  | "sharpe"
  | "sortino"
  | "performance"
  | "correlation"
  | "covariance"
  | "correlation_matrix"
  | "covariance_matrix"
  | "beta"
  | "monte_carlo"
  | "scenario"
  | "backtest";

export type ReturnsMethod = "simple" | "log";

export interface AnalysisRequest {
  method: AnalysisMethod;
  prices?: number[];
  returns?: number[];
  returns_method?: ReturnsMethod;
  annualization_factor?: number;
  risk_free_rate?: number;
  target?: number;
  confidence?: number;
  returns_a?: number[];
  returns_b?: number[];
  asset_returns?: number[];
  benchmark_returns?: number[];
  multi_returns?: number[][];
  labels?: string[];
  initial_value?: number;
  mu?: number;
  sigma?: number;
  horizon?: number;
  n_simulations?: number;
  seed?: number | null;
  weights?: number[];
  shocks?: number[];
  strategy_returns?: number[];
}

export interface AnalysisResponse {
  method: string;
  result: Record<string, unknown>;
  metadata: Record<string, unknown>;
  error?: string | null;
}

export interface HealthResponse {
  status: string;
  version: string;
}

/** Normalized chart series for line / area charts */
export interface ChartPoint {
  x: number | string;
  y: number;
}

export interface ChartSeries {
  id: string;
  label: string;
  data: ChartPoint[];
  color?: string;
}

/** Analysis UI state machine */
export type AnalysisStatus =
  | "idle"
  | "editing"
  | "loading"
  | "success"
  | "error"
  | "empty"
  | "invalid";

export interface MethodMeta {
  id: AnalysisMethod;
  label: string;
  description: string;
  category: "returns" | "risk" | "performance" | "relationship" | "simulation" | "research";
  needsPrices?: boolean;
  needsReturns?: boolean;
  needsTwoSeries?: boolean;
  needsMulti?: boolean;
  needsScenario?: boolean;
  needsMonteCarlo?: boolean;
  needsConfidence?: boolean;
  needsBenchmark?: boolean;
}

export const METHODS: MethodMeta[] = [
  { id: "returns", label: "Returns", description: "Simple and log returns, cumulative path", category: "returns", needsPrices: true },
  { id: "volatility", label: "Volatility", description: "Daily and annualized volatility", category: "risk", needsReturns: true },
  { id: "drawdown", label: "Drawdown", description: "Drawdown series, max drawdown, duration", category: "risk", needsReturns: true },
  { id: "var", label: "VaR", description: "Historical Value-at-Risk (positive loss)", category: "risk", needsReturns: true, needsConfidence: true },
  { id: "cvar", label: "CVaR", description: "Historical Expected Shortfall", category: "risk", needsReturns: true, needsConfidence: true },
  { id: "risk", label: "Risk (VaR + CVaR)", description: "Combined historical risk metrics", category: "risk", needsReturns: true, needsConfidence: true },
  { id: "sharpe", label: "Sharpe Ratio", description: "Risk-adjusted return vs risk-free rate", category: "performance", needsReturns: true },
  { id: "sortino", label: "Sortino Ratio", description: "Downside risk-adjusted return", category: "performance", needsReturns: true },
  { id: "performance", label: "Performance", description: "Sharpe and Sortino together", category: "performance", needsReturns: true },
  { id: "correlation", label: "Correlation", description: "Pearson correlation of two series", category: "relationship", needsTwoSeries: true },
  { id: "covariance", label: "Covariance", description: "Sample covariance of two series", category: "relationship", needsTwoSeries: true },
  { id: "correlation_matrix", label: "Correlation Matrix", description: "Multi-asset correlation matrix", category: "relationship", needsMulti: true },
  { id: "covariance_matrix", label: "Covariance Matrix", description: "Multi-asset covariance matrix", category: "relationship", needsMulti: true },
  { id: "beta", label: "Beta", description: "Asset beta vs benchmark", category: "relationship", needsTwoSeries: true, needsBenchmark: true },
  { id: "monte_carlo", label: "Monte Carlo", description: "Path simulation and distribution", category: "simulation", needsMonteCarlo: true },
  { id: "scenario", label: "Scenario", description: "Deterministic shock impact", category: "simulation", needsScenario: true },
  { id: "backtest", label: "Backtest", description: "Strategy metrics vs optional benchmark", category: "research", needsReturns: true, needsBenchmark: true },
];
