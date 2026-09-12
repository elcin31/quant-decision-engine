"use client";

import { useCallback, useState } from "react";
import { runAnalysis, ApiError } from "@/services/api";
import type { AnalysisRequest, AnalysisResponse, AnalysisStatus } from "@/types/analysis";

export function useAnalysis() {
  const [status, setStatus] = useState<AnalysisStatus>("idle");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (request: AnalysisRequest) => {
    setStatus("loading");
    setError(null);
    setResult(null);
    try {
      const res = await runAnalysis(request);
      setResult(res);
      setStatus("success");
      return res;
    } catch (e) {
      const message = e instanceof ApiError ? e.detail : "Request failed.";
      setError(message);
      setStatus("error");
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus("idle");
    setResult(null);
    setError(null);
  }, []);

  return { status, result, error, execute, reset, setStatus };
}
