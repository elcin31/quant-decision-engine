"use client";

import { useMemo, useState } from "react";
import type { AnalysisMethod, AnalysisRequest, MethodMeta } from "@/types/analysis";
import { METHODS } from "@/types/analysis";
import {
  parseNumberList,
  sampleBenchmarkReturns,
  sampleMultiReturns,
  samplePrices,
  sampleReturns,
} from "@/lib/sampleData";

interface AnalysisFormProps {
  initialMethod?: AnalysisMethod;
  onSubmit: (req: AnalysisRequest) => void;
  onMethodChange?: (method: AnalysisMethod) => void;
  loading?: boolean;
}

export function AnalysisForm({ initialMethod = "volatility", onSubmit, onMethodChange, loading }: AnalysisFormProps) {
  const [method, setMethod] = useState<AnalysisMethod>(initialMethod);
  const meta = useMemo(() => METHODS.find((m) => m.id === method)!, [method]);

  const [returnsText, setReturnsText] = useState(() => sampleReturns(40).map((x) => x.toFixed(6)).join("\n"));
  const [pricesText, setPricesText] = useState(() => samplePrices(41).map((x) => x.toFixed(4)).join("\n"));
  const [returnsAText, setReturnsAText] = useState(() => sampleReturns(40, 1).map((x) => x.toFixed(6)).join("\n"));
  const [returnsBText, setReturnsBText] = useState(() => sampleBenchmarkReturns(40).map((x) => x.toFixed(6)).join("\n"));
  const [confidence, setConfidence] = useState(0.95);
  const [annFactor, setAnnFactor] = useState(252);
  const [riskFree, setRiskFree] = useState(0);
  const [target, setTarget] = useState(0);
  const [initialValue, setInitialValue] = useState(100);
  const [mu, setMu] = useState(0.0004);
  const [sigma, setSigma] = useState(0.012);
  const [horizon, setHorizon] = useState(63);
  const [nSim, setNSim] = useState(2000);
  const [seed, setSeed] = useState(42);
  const [weightsText, setWeightsText] = useState("0.25, 0.25, 0.25, 0.25");
  const [shocksText, setShocksText] = useState("-0.20, -0.10, 0.05, -0.05");
  const [labelsText, setLabelsText] = useState("A, B, C, D");
  const [usePrices, setUsePrices] = useState(false);

  function loadSample() {
    setReturnsText(sampleReturns(40).map((x) => x.toFixed(6)).join("\n"));
    setPricesText(samplePrices(41).map((x) => x.toFixed(4)).join("\n"));
    setReturnsAText(sampleReturns(40, 1).map((x) => x.toFixed(6)).join("\n"));
    setReturnsBText(sampleBenchmarkReturns(40).map((x) => x.toFixed(6)).join("\n"));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const req: AnalysisRequest = { method, annualization_factor: annFactor };

    if (meta.needsConfidence) req.confidence = confidence;
    if (meta.needsReturns || meta.needsPrices) {
      if (usePrices || meta.needsPrices) {
        req.prices = parseNumberList(pricesText);
      } else {
        req.returns = parseNumberList(returnsText);
      }
    }
    if (meta.id === "sharpe" || meta.id === "performance" || meta.id === "backtest") {
      req.risk_free_rate = riskFree;
    }
    if (meta.id === "sortino" || meta.id === "performance") {
      req.target = target;
    }
    if (meta.needsTwoSeries || meta.needsBenchmark) {
      if (meta.id === "beta" || meta.id === "backtest") {
        req.asset_returns = parseNumberList(returnsAText);
        req.strategy_returns = parseNumberList(returnsAText);
        req.benchmark_returns = parseNumberList(returnsBText);
        req.returns_a = parseNumberList(returnsAText);
        req.returns_b = parseNumberList(returnsBText);
      } else {
        req.returns_a = parseNumberList(returnsAText);
        req.returns_b = parseNumberList(returnsBText);
      }
    }
    if (meta.needsMulti) {
      req.multi_returns = sampleMultiReturns(40);
      req.labels = ["Asset A", "Asset B", "Asset C"];
    }
    if (meta.needsMonteCarlo) {
      req.initial_value = initialValue;
      req.mu = mu;
      req.sigma = sigma;
      req.horizon = horizon;
      req.n_simulations = nSim;
      req.seed = seed;
    }
    if (meta.needsScenario) {
      req.weights = parseNumberList(weightsText);
      req.shocks = parseNumberList(shocksText);
      req.labels = labelsText.split(/[\s,;]+/).filter(Boolean);
    }
    onSubmit(req);
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="card-title">Configure research</div>

      <div className="field">
        <label>Analysis method</label>
        <div className="method-select" role="listbox" aria-label="Analysis method">
          {METHODS.map((m) => (
            <button
              key={m.id}
              type="button"
              className={`method-option ${method === m.id ? "active" : ""}`}
              onClick={() => {
                setMethod(m.id);
                onMethodChange?.(m.id);
              }}
              aria-selected={method === m.id}
              role="option"
            >
              <span>{m.label}</span>
            </button>
          ))}
        </div>
        <p className="field-hint">{meta.description}</p>
      </div>

      {(meta.needsReturns || meta.needsPrices) && !meta.needsTwoSeries && !meta.needsMonteCarlo && !meta.needsScenario && (
        <>
          {!meta.needsPrices && (
            <div className="field">
              <label>
                <input
                  type="checkbox"
                  checked={usePrices}
                  onChange={(e) => setUsePrices(e.target.checked)}
                  style={{ width: "auto", marginRight: 8 }}
                />
                Use prices instead of returns
              </label>
            </div>
          )}
          {(usePrices || meta.needsPrices) ? (
            <div className="field">
              <label htmlFor="prices">Prices (one per line or comma-separated)</label>
              <textarea id="prices" value={pricesText} onChange={(e) => setPricesText(e.target.value)} rows={5} />
            </div>
          ) : (
            <div className="field">
              <label htmlFor="returns">Returns (one per line or comma-separated)</label>
              <textarea id="returns" value={returnsText} onChange={(e) => setReturnsText(e.target.value)} rows={5} />
            </div>
          )}
        </>
      )}

      {(meta.needsTwoSeries || (meta.needsBenchmark && meta.id !== "backtest")) && (
        <>
          <div className="field">
            <label htmlFor="ra">{meta.id === "beta" ? "Asset returns" : "Series A"}</label>
            <textarea id="ra" value={returnsAText} onChange={(e) => setReturnsAText(e.target.value)} rows={4} />
          </div>
          <div className="field">
            <label htmlFor="rb">{meta.id === "beta" ? "Benchmark returns" : "Series B"}</label>
            <textarea id="rb" value={returnsBText} onChange={(e) => setReturnsBText(e.target.value)} rows={4} />
          </div>
        </>
      )}

      {meta.id === "backtest" && (
        <>
          <div className="field">
            <label htmlFor="strat">Strategy returns</label>
            <textarea id="strat" value={returnsAText} onChange={(e) => setReturnsAText(e.target.value)} rows={4} />
          </div>
          <div className="field">
            <label htmlFor="bench">Benchmark returns (optional)</label>
            <textarea id="bench" value={returnsBText} onChange={(e) => setReturnsBText(e.target.value)} rows={4} />
          </div>
        </>
      )}

      {meta.needsMulti && (
        <p className="field-hint">Multi-asset matrix uses built-in sample series (3 assets × 40 observations).</p>
      )}

      {meta.needsConfidence && (
        <div className="field">
          <label htmlFor="conf">Confidence level</label>
          <select id="conf" value={confidence} onChange={(e) => setConfidence(Number(e.target.value))}>
            <option value={0.9}>90%</option>
            <option value={0.95}>95%</option>
            <option value={0.99}>99%</option>
          </select>
        </div>
      )}

      {(meta.id === "volatility" || meta.id === "sharpe" || meta.id === "sortino" || meta.id === "performance" || meta.id === "backtest") && (
        <div className="field">
          <label htmlFor="ann">Annualization factor</label>
          <input id="ann" type="number" min={1} value={annFactor} onChange={(e) => setAnnFactor(Number(e.target.value))} />
        </div>
      )}

      {(meta.id === "sharpe" || meta.id === "performance" || meta.id === "backtest") && (
        <div className="field">
          <label htmlFor="rf">Risk-free rate (per period)</label>
          <input id="rf" type="number" step="any" value={riskFree} onChange={(e) => setRiskFree(Number(e.target.value))} />
        </div>
      )}

      {(meta.id === "sortino" || meta.id === "performance") && (
        <div className="field">
          <label htmlFor="tgt">Target return (per period)</label>
          <input id="tgt" type="number" step="any" value={target} onChange={(e) => setTarget(Number(e.target.value))} />
        </div>
      )}

      {meta.needsMonteCarlo && (
        <div className="grid-2">
          <div className="field">
            <label htmlFor="iv">Initial value</label>
            <input id="iv" type="number" min={0.01} step="any" value={initialValue} onChange={(e) => setInitialValue(Number(e.target.value))} />
          </div>
          <div className="field">
            <label htmlFor="mu">μ (drift per period)</label>
            <input id="mu" type="number" step="any" value={mu} onChange={(e) => setMu(Number(e.target.value))} />
          </div>
          <div className="field">
            <label htmlFor="sig">σ (vol per period)</label>
            <input id="sig" type="number" min={0} step="any" value={sigma} onChange={(e) => setSigma(Number(e.target.value))} />
          </div>
          <div className="field">
            <label htmlFor="hor">Horizon (periods)</label>
            <input id="hor" type="number" min={1} value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} />
          </div>
          <div className="field">
            <label htmlFor="ns">Simulations</label>
            <input id="ns" type="number" min={1} max={100000} value={nSim} onChange={(e) => setNSim(Number(e.target.value))} />
          </div>
          <div className="field">
            <label htmlFor="seed">Random seed</label>
            <input id="seed" type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
          </div>
        </div>
      )}

      {meta.needsScenario && (
        <>
          <div className="field">
            <label htmlFor="w">Weights (comma-separated)</label>
            <input id="w" value={weightsText} onChange={(e) => setWeightsText(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="sh">Shocks (comma-separated, e.g. -0.20 = −20%)</label>
            <input id="sh" value={shocksText} onChange={(e) => setShocksText(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="lb">Labels</label>
            <input id="lb" value={labelsText} onChange={(e) => setLabelsText(e.target.value)} />
          </div>
        </>
      )}

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Computing…" : "Run analysis"}
        </button>
        <button type="button" className="btn btn-secondary" onClick={loadSample} disabled={loading}>
          Load sample data
        </button>
      </div>
    </form>
  );
}
