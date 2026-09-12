"""Pydantic request models for the analysis API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    """
    Generic analysis request.

    The `method` field selects the quantitative routine.
    Additional fields are method-specific; unknown fields are ignored
    by the dispatcher after validation of required ones.
    """

    method: Literal[
        "returns",
        "volatility",
        "drawdown",
        "var",
        "cvar",
        "risk",
        "sharpe",
        "sortino",
        "performance",
        "correlation",
        "covariance",
        "correlation_matrix",
        "covariance_matrix",
        "beta",
        "monte_carlo",
        "scenario",
        "backtest",
    ]

    prices: list[float] | None = None
    returns: list[float] | None = None
    returns_method: Literal["simple", "log"] = "simple"

    annualization_factor: int = Field(default=252, gt=0)
    risk_free_rate: float = 0.0
    target: float = 0.0

    confidence: float = Field(default=0.95, gt=0.0, lt=1.0)

    returns_a: list[float] | None = None
    returns_b: list[float] | None = None
    asset_returns: list[float] | None = None
    benchmark_returns: list[float] | None = None
    multi_returns: list[list[float]] | None = None
    labels: list[str] | None = None

    initial_value: float = Field(default=100.0, gt=0)
    mu: float | None = None
    sigma: float | None = None
    horizon: int = Field(default=252, ge=1)
    n_simulations: int = Field(default=10_000, ge=1, le=100_000)
    seed: int | None = None

    weights: list[float] | None = None
    shocks: list[float] | None = None

    strategy_returns: list[float] | None = None

    @field_validator("confidence")
    @classmethod
    def check_confidence(cls, v: float) -> float:
        if not 0.0 < v < 1.0:
            raise ValueError("confidence must be in (0, 1)")
        return v


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
