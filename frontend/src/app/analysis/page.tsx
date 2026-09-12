"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import { AnalysisForm } from "@/components/analysis/AnalysisForm";
import { AnalysisResult } from "@/components/analysis/AnalysisResult";
import { StateBox } from "@/components/ui/StateBox";
import { useAnalysis } from "@/hooks/useAnalysis";
import type { AnalysisMethod, AnalysisRequest } from "@/types/analysis";
import { METHODS } from "@/types/analysis";

function AnalysisPageInner() {
  const params = useSearchParams();
  const methodParam = params.get("method") as AnalysisMethod | null;
  const initial = (methodParam && METHODS.some((m) => m.id === methodParam)
    ? methodParam
    : "volatility") as AnalysisMethod;
  const [selectedMethod, setSelectedMethod] = useState<AnalysisMethod>(initial);
  const { status, result, error, execute } = useAnalysis();

  const active = useMemo(
    () => METHODS.find((m) => m.id === selectedMethod) ?? METHODS[0]!,
    [selectedMethod]
  );
  const methodIndex = String(METHODS.findIndex((m) => m.id === active.id) + 1).padStart(2, "0");

  async function handleSubmit(req: AnalysisRequest) {
    await execute(req);
  }

  return (
    <div className="analysis-workspace">
      <div className="analysis-topbar">
        <div>
          <div className="eyebrow">RESEARCH / ANALYSIS</div>
          <h1>New analysis</h1>
          <p>Configure a method, provide observations, and inspect the result.</p>
        </div>
        <div className="engine-badge">
          <span className="status-dot" /> ENGINE READY
        </div>
      </div>

      <div className="analysis-layout">
        <aside className="analysis-sidebar" aria-label="Active method">
          <div className="sidebar-label">METHOD</div>
          <div className="active-method">
            <span className="method-number">{methodIndex}</span>
            <div>
              <strong>{active.label}</strong>
              <span>{active.category}</span>
            </div>
          </div>
          <div className="sidebar-rule" />
          <p className="sidebar-note">
            Calculations execute in the Python quantitative engine. The browser only collects
            inputs and renders results.
          </p>
          <div className="sidebar-spec">
            <span>DEFAULT</span>
            <b>252 periods</b>
            <span>DATA</span>
            <b>Sample / manual</b>
            <span>OUTPUT</span>
            <b>JSON + charts</b>
          </div>
        </aside>

        <main className="analysis-main">
          <AnalysisForm
            initialMethod={initial}
            onSubmit={handleSubmit}
            onMethodChange={setSelectedMethod}
            loading={status === "loading"}
          />

          <div className="result-panel">
            <div className="result-heading">
              <span>RESULT</span>
              {status === "success" && <b>COMPUTED</b>}
              {status === "loading" && <b>RUNNING</b>}
              {status === "error" && <b style={{ color: "var(--negative)" }}>ERROR</b>}
            </div>
            <div className="result-body">
              {status === "idle" && (
                <StateBox variant="empty">
                  <span className="state-symbol">∑</span>
                  <strong>Awaiting analysis</strong>
                  <span>Configure the inputs and run the calculation.</span>
                </StateBox>
              )}
              {status === "loading" && (
                <StateBox variant="loading">
                  <span className="state-symbol spinning">◌</span>
                  <strong>Computing</strong>
                  <span>Sending inputs to the quantitative engine…</span>
                </StateBox>
              )}
              {status === "error" && error && (
                <StateBox variant="error">
                  <strong>Unable to complete analysis</strong>
                  <span>{error}</span>
                </StateBox>
              )}
              {status === "success" && result && <AnalysisResult response={result} />}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense
      fallback={
        <StateBox variant="loading">
          <span className="state-symbol spinning">◌</span>
          <strong>Loading workspace…</strong>
        </StateBox>
      }
    >
      <AnalysisPageInner />
    </Suspense>
  );
}
