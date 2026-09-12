"""FastAPI application entry point for Quant Decision Engine."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.models.requests import HealthResponse

app = FastAPI(
    title="Quant Decision Engine",
    description=(
        "Quantitative research and decision-support calculation engine. "
        "Provides returns, volatility, drawdown, VaR/CVaR, Sharpe/Sortino, "
        "correlation, beta, Monte Carlo, scenario analysis, and basic backtesting."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/")
def root() -> dict:
    return {
        "name": "Quant Decision Engine",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "analysis": "POST /api/analysis",
    }
