/**
 * Centralized API client for Quant Decision Engine backend.
 * All network calls go through this module.
 */

import type { AnalysisRequest, AnalysisResponse, HealthResponse } from "@/types/analysis";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function humanizeError(detail: unknown): string {
  if (typeof detail === "string") {
    if (detail.includes("length mismatch")) {
      return "The series have different lengths. Ensure both cover the same observations.";
    }
    if (detail.includes("empty") || detail.includes("Insufficient")) {
      return "Not enough observations to compute this metric. Provide more data points.";
    }
    if (detail.includes("constant")) {
      return "One or more series are constant; correlation and related metrics are undefined.";
    }
    if (detail.includes("zero") && detail.includes("variance")) {
      return "Benchmark variance is zero; beta cannot be computed.";
    }
    if (detail.includes("positive")) {
      return "Prices must be strictly positive.";
    }
    if (detail.includes("confidence")) {
      return "Confidence level must be between 0 and 1 (e.g. 0.95).";
    }
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "object" && d && "msg" in d ? String((d as { msg: string }).msg) : String(d)))
      .join("; ");
  }
  if (detail && typeof detail === "object" && "detail" in detail) {
    return humanizeError((detail as { detail: unknown }).detail);
  }
  return "An unexpected error occurred. Check your inputs and try again.";
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  let res: Response;
  try {
    res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(options?.headers ?? {}),
      },
    });
  } catch {
    throw new ApiError(
      0,
      "Cannot reach the analysis server. Ensure the backend is running on " + API_BASE
    );
  }

  let body: unknown;
  try {
    body = await res.json();
  } catch {
    throw new ApiError(res.status, "Invalid response from server.");
  }

  if (!res.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? (body as { detail: unknown }).detail
        : body;
    throw new ApiError(res.status, humanizeError(detail));
  }

  return body as T;
}

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function runAnalysis(payload: AnalysisRequest): Promise<AnalysisResponse> {
  return request<AnalysisResponse>("/api/analysis", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getApiBase(): string {
  return API_BASE;
}
