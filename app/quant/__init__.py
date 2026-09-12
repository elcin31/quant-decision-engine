"""Quantitative calculation engine."""

from app.quant.returns import (
    simple_returns,
    log_returns,
    cumulative_return,
    cumulative_return_series,
    returns_from_prices,
)
from app.quant.volatility import daily_volatility, annualized_volatility, volatility_metrics
from app.quant.drawdown import (
    drawdown_series,
    maximum_drawdown,
    drawdown_duration,
    drawdown_metrics,
)
from app.quant.risk import historical_var, historical_cvar, risk_metrics
from app.quant.performance import sharpe_ratio, sortino_ratio, performance_metrics
from app.quant.correlation import (
    pearson_correlation,
    covariance,
    correlation_matrix,
    covariance_matrix,
)
from app.quant.beta import beta, beta_metrics
from app.quant.monte_carlo import simulate_paths
from app.quant.scenarios import single_asset_impact, portfolio_scenario
from app.quant.backtest import cagr, run_backtest

__all__ = [
    "simple_returns",
    "log_returns",
    "cumulative_return",
    "cumulative_return_series",
    "returns_from_prices",
    "daily_volatility",
    "annualized_volatility",
    "volatility_metrics",
    "drawdown_series",
    "maximum_drawdown",
    "drawdown_duration",
    "drawdown_metrics",
    "historical_var",
    "historical_cvar",
    "risk_metrics",
    "sharpe_ratio",
    "sortino_ratio",
    "performance_metrics",
    "pearson_correlation",
    "covariance",
    "correlation_matrix",
    "covariance_matrix",
    "beta",
    "beta_metrics",
    "simulate_paths",
    "single_asset_impact",
    "portfolio_scenario",
    "cagr",
    "run_backtest",
]
