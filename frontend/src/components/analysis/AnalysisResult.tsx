"use client";

import type { AnalysisResponse } from "@/types/analysis";
import { Metric } from "@/components/ui/Metric";
import { LineChart } from "@/components/charts/LineChart";
import { Histogram } from "@/components/charts/Histogram";
import { PathChart } from "@/components/charts/PathChart";
import { formatNumber, formatPct } from "@/lib/sampleData";

interface Props {
  response: AnalysisResponse;
}

function num(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null;
}

function numArr(v: unknown): number[] {
  return Array.isArray(v) ? v.filter((x): x is number => typeof x === "number") : [];
}

export function AnalysisResult({ response }: Props) {
  const { method, result, metadata } = response;
  const r = result as Record<string, unknown>;

  return (
    <div className="stack">
      {renderBody(method, r)}
      {metadata && Object.keys(metadata).length > 0 && (
        <p className="text-sm text-dim mt-4 mono">
          {Object.entries(metadata)
            .map(([k, v]) => `${k}: ${String(v)}`)
            .join(" · ")}
        </p>
      )}
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="card-title" style={{ marginTop: 18, marginBottom: 10 }}>
      {children}
    </div>
  );
}

function renderBody(method: string, r: Record<string, unknown>) {
  switch (method) {
    case "returns":
      return (
        <>
          <div className="metric-row mb-4">
            <Metric label="Total cumulative" value={num(r.total_cumulative_return)} format="pct" signed />
          </div>
          {numArr(r.cumulative_return_series).length > 0 && (
            <>
              <SectionLabel>Cumulative path</SectionLabel>
              <LineChart
                series={[{ id: "cum", label: "Cumulative return", values: numArr(r.cumulative_return_series) }]}
                yFormat={(v) => formatPct(v, 1)}
              />
            </>
          )}
        </>
      );

    case "volatility":
      return (
        <div className="metric-row">
          <Metric label="Daily vol" value={num(r.daily)} format="pct" />
          <Metric label="Annualized vol" value={num(r.annualized)} format="pct" />
          <Metric label="Observations" value={num(r.observations)} format="raw" digits={0} />
        </div>
      );

    case "drawdown":
      return (
        <>
          <div className="metric-row mb-4">
            <Metric label="Max drawdown" value={num(r.max_drawdown)} format="pct" signed />
            <Metric label="Duration (periods)" value={num(r.duration_periods)} format="raw" digits={0} />
            <Metric label="Underwater periods" value={num(r.underwater_periods)} format="raw" digits={0} />
          </div>
          {numArr(r.drawdown_series).length > 0 && (
            <>
              <SectionLabel>Drawdown series</SectionLabel>
              <LineChart
                series={[{ id: "dd", label: "Drawdown", values: numArr(r.drawdown_series), color: "#ff6b72" }]}
                yFormat={(v) => formatPct(v, 1)}
              />
            </>
          )}
        </>
      );

    case "var":
    case "cvar":
    case "risk":
      return (
        <>
          <div className="metric-row">
            {"var" in r && <Metric label="VaR" value={num(r.var)} format="pct" />}
            {"cvar" in r && <Metric label="CVaR" value={num(r.cvar)} format="pct" />}
            {"confidence" in r && (
              <Metric label="Confidence" value={num(r.confidence)} format="pct" digits={0} />
            )}
          </div>
          <p className="text-sm text-dim mt-4">Convention: positive values represent potential loss.</p>
        </>
      );

    case "sharpe":
    case "sortino":
    case "performance":
      return (
        <div className="metric-row">
          {"sharpe" in r && <Metric label="Sharpe" value={num(r.sharpe)} />}
          {"sharpe_annualized" in r && <Metric label="Sharpe (ann.)" value={num(r.sharpe_annualized)} />}
          {"sortino" in r && <Metric label="Sortino" value={num(r.sortino)} />}
          {"sortino_annualized" in r && <Metric label="Sortino (ann.)" value={num(r.sortino_annualized)} />}
          {"mean_return" in r && <Metric label="Mean return" value={num(r.mean_return)} format="pct" signed />}
        </div>
      );

    case "correlation":
    case "covariance":
      return (
        <div className="metric-row">
          {"correlation" in r && <Metric label="Correlation" value={num(r.correlation)} />}
          {"covariance" in r && <Metric label="Covariance" value={num(r.covariance)} />}
        </div>
      );

    case "correlation_matrix":
    case "covariance_matrix":
      return <MatrixView matrix={r.matrix as number[][]} labels={(r.labels as string[]) ?? []} />;

    case "beta":
      return (
        <div className="metric-row">
          <Metric label="Beta" value={num(r.beta)} />
          <Metric label="Asset vol" value={num(r.asset_vol)} format="pct" />
          <Metric label="Benchmark vol" value={num(r.benchmark_vol)} format="pct" />
        </div>
      );

    case "monte_carlo":
      return <MonteCarloView r={r} />;

    case "scenario":
      return <ScenarioView r={r} />;

    case "backtest":
      return <BacktestView r={r} />;

    default:
      return (
        <pre className="mono text-sm" style={{ overflow: "auto", maxHeight: 320 }}>
          {JSON.stringify(r, null, 2)}
        </pre>
      );
  }
}

function MatrixView({ matrix, labels }: { matrix: number[][]; labels: string[] }) {
  if (!matrix?.length) return <div className="state-box">Empty matrix</div>;
  return (
    <div className="matrix-wrap">
      <table className="matrix-table">
        <thead>
          <tr>
            <th />
            {labels.map((l) => (
              <th key={l}>{l}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              <th>{labels[i] ?? i}</th>
              {row.map((v, j) => (
                <td key={j}>{formatNumber(v, 3)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MonteCarloView({ r }: { r: Record<string, unknown> }) {
  const paths = (r.sample_paths as number[][]) ?? [];
  const dist = r.final_distribution as { bin_edges?: number[]; counts?: number[] } | undefined;
  const pct = (r.percentiles as Record<string, number>) ?? {};
  return (
    <>
      <div className="metric-row mb-4">
        <Metric label="Final mean" value={num(r.final_mean)} />
        <Metric label="Final median" value={num(r.final_median)} />
        <Metric label="P(loss)" value={num(r.probability_of_loss)} format="pct" />
        <Metric label="Expected return" value={num(r.expected_return)} format="pct" signed />
        <Metric label="P5" value={num(pct.p5)} />
        <Metric label="P95" value={num(pct.p95)} />
      </div>
      <SectionLabel>Simulated paths</SectionLabel>
      <PathChart paths={paths} initialValue={num(r.initial_value) ?? undefined} maxPaths={40} />
      {dist?.bin_edges && dist.counts && (
        <>
          <SectionLabel>Final value distribution</SectionLabel>
          <Histogram
            binEdges={dist.bin_edges}
            counts={dist.counts}
            highlight={num(r.final_median) ?? undefined}
          />
        </>
      )}
    </>
  );
}

function ScenarioView({ r }: { r: Record<string, unknown> }) {
  const contribs =
    (r.contributions as { label: string; weight: number; shock: number; contribution: number }[]) ??
    [];
  const total = num(r.total_impact);
  return (
    <>
      <div className="metric-row mb-4">
        <Metric label="Total portfolio impact" value={total} format="pct" signed />
      </div>
      <div className="scenario-panel">
        <div>
          <h4>Baseline assumptions</h4>
          <ul className="scenario-list">
            {contribs.map((c) => (
              <li key={c.label}>
                {c.label}: weight {formatNumber(c.weight, 2)}, shock {formatPct(c.shock)}
              </li>
            ))}
          </ul>
          <p className="text-sm text-dim mt-4">{String(r.note ?? r.assumption ?? "")}</p>
        </div>
        <div>
          <h4>Scenario impact</h4>
          <ul className="scenario-list">
            {contribs.map((c) => (
              <li key={c.label}>
                {c.label}: contribution {formatPct(c.contribution)}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}

function BacktestView({ r }: { r: Record<string, unknown> }) {
  const strat = (r.strategy as Record<string, unknown>) ?? {};
  const bench = r.benchmark as Record<string, unknown> | undefined;
  const series: { id: string; label: string; values: number[]; color?: string }[] = [];
  const sc = numArr(strat.cumulative_return_series);
  if (sc.length) series.push({ id: "s", label: "Strategy", values: sc });
  if (bench) {
    const bc = numArr(bench.cumulative_return_series);
    if (bc.length) series.push({ id: "b", label: "Benchmark", values: bc, color: "#8c9399" });
  }
  return (
    <>
      <div className="metric-row mb-4">
        <Metric label="Total return" value={num(strat.total_return)} format="pct" signed />
        <Metric label="CAGR" value={num(strat.cagr)} format="pct" signed />
        <Metric label="Ann. vol" value={num(strat.annualized_volatility)} format="pct" />
        <Metric label="Sharpe (ann.)" value={num(strat.sharpe_annualized)} />
        <Metric label="Max drawdown" value={num(strat.max_drawdown)} format="pct" signed />
      </div>
      {series.length > 0 && (
        <>
          <SectionLabel>Cumulative returns</SectionLabel>
          <LineChart series={series} yFormat={(v) => formatPct(v, 1)} />
        </>
      )}
      {bench && (
        <p className="text-sm text-dim mt-4 mono">
          Benchmark total: {formatPct(num(bench.total_return))} · CAGR: {formatPct(num(bench.cagr))}
        </p>
      )}
    </>
  );
}
