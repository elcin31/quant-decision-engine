"""Minimal backtesting / performance attribution engine.

Accepts pre-computed strategy returns and optional benchmark returns.
Computes standard research metrics. No order execution or broker logic.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.config import DEFAULT_ANNUALIZATION_FACTOR, MIN_OBSERVATIONS
from app.quant.drawdown import maximum_drawdown
from app.quant.performance import sharpe_ratio
from app.quant.returns import cumulative_return, cumulative_return_series
from app.quant.utils import QuantValidationError, to_float_list, to_python_scalar, validate_series
from app.quant.volatility import annualized_volatility


def cagr(
    returns: Sequence[float] | np.ndarray,
    periods_per_year: int = DEFAULT_ANNUALIZATION_FACTOR,
) -> float:
    """
    Compound Annual Growth Rate from a return series.

    total_return = prod(1+r) - 1
    years = n_periods / periods_per_year
    CAGR = (1 + total_return)^(1/years) - 1
    """
    r = validate_series(returns, name="returns", min_length=1)
    if periods_per_year <= 0:
        raise QuantValidationError("periods_per_year must be positive")
    if (r <= -1.0).any():
        raise QuantValidationError("returns contain values <= -1")
    total = float(np.prod(1.0 + r) - 1.0)
    n = r.size
    years = n / periods_per_year
    if years <= 0:
        raise QuantValidationError("Effective years must be positive")
    if total <= -1.0:
        return -1.0
    return float((1.0 + total) ** (1.0 / years) - 1.0)


def run_backtest(
    strategy_returns: Sequence[float] | np.ndarray,
    benchmark_returns: Sequence[float] | np.ndarray | None = None,
    risk_free_rate: float = 0.0,
    annualization_factor: int = DEFAULT_ANNUALIZATION_FACTOR,
) -> dict:
    """
    Compute research metrics for a strategy (and optional benchmark).

    All inputs are period returns (same frequency).
    """
    strat = validate_series(
        strategy_returns, name="strategy_returns", min_length=MIN_OBSERVATIONS
    )
    if annualization_factor <= 0:
        raise QuantValidationError("annualization_factor must be positive")

    cum_series = cumulative_return_series(strat)
    total_ret = cumulative_return(strat)
    ann_vol = annualized_volatility(strat, annualization_factor)
    sharpe = sharpe_ratio(strat, risk_free_rate=risk_free_rate, annualization_factor=annualization_factor)
    max_dd = maximum_drawdown(returns=strat)
    cagr_val = cagr(strat, periods_per_year=annualization_factor)

    result: dict = {
        "strategy": {
            "total_return": to_python_scalar(total_ret),
            "cagr": to_python_scalar(cagr_val),
            "annualized_volatility": to_python_scalar(ann_vol),
            "sharpe_annualized": to_python_scalar(sharpe),
            "max_drawdown": to_python_scalar(max_dd),
            "cumulative_return_series": to_float_list(cum_series),
            "observations": int(strat.size),
        },
        "risk_free_rate": float(risk_free_rate),
        "annualization_factor": int(annualization_factor),
    }

    if benchmark_returns is not None:
        bench = validate_series(
            benchmark_returns, name="benchmark_returns", min_length=MIN_OBSERVATIONS
        )
        if bench.size != strat.size:
            raise QuantValidationError(
                f"strategy and benchmark length mismatch: {strat.size} vs {bench.size}"
            )
        bench_cum = cumulative_return_series(bench)
        bench_total = cumulative_return(bench)
        bench_vol = annualized_volatility(bench, annualization_factor)
        bench_sharpe = sharpe_ratio(
            bench, risk_free_rate=risk_free_rate, annualization_factor=annualization_factor
        )
        bench_dd = maximum_drawdown(returns=bench)
        bench_cagr = cagr(bench, periods_per_year=annualization_factor)

        excess = strat - bench
        excess_total = cumulative_return(excess) if not (excess <= -1).any() else None

        result["benchmark"] = {
            "total_return": to_python_scalar(bench_total),
            "cagr": to_python_scalar(bench_cagr),
            "annualized_volatility": to_python_scalar(bench_vol),
            "sharpe_annualized": to_python_scalar(bench_sharpe),
            "max_drawdown": to_python_scalar(bench_dd),
            "cumulative_return_series": to_float_list(bench_cum),
            "observations": int(bench.size),
        }
        result["relative"] = {
            "excess_total_return": to_python_scalar(excess_total) if excess_total is not None else None,
            "active_return_mean": to_python_scalar(float(np.mean(excess))),
        }

    return result
