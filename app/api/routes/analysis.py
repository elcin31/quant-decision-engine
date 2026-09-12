"""Analysis API routes – thin layer over the quant engine."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.requests import AnalysisRequest
from app.models.responses import AnalysisResponse
from app.quant import (
    annualized_volatility,
    beta_metrics,
    correlation_matrix,
    covariance,
    covariance_matrix,
    cumulative_return,
    cumulative_return_series,
    daily_volatility,
    drawdown_metrics,
    historical_cvar,
    historical_var,
    log_returns,
    pearson_correlation,
    performance_metrics,
    portfolio_scenario,
    returns_from_prices,
    risk_metrics,
    run_backtest,
    sharpe_ratio,
    simple_returns,
    simulate_paths,
    sortino_ratio,
    volatility_metrics,
)
from app.quant.utils import QuantValidationError, to_float_list

router = APIRouter(prefix="/api", tags=["analysis"])


def _require(value, name: str):
    if value is None:
        raise QuantValidationError(f"'{name}' is required for this method")
    return value


@router.post("/analysis", response_model=AnalysisResponse)
def run_analysis(req: AnalysisRequest) -> AnalysisResponse:
    """
    Dispatch quantitative calculation based on `method`.

    All results are JSON-serializable.
    """
    method = req.method
    try:
        result, metadata = _dispatch(req)
        return AnalysisResponse(method=method, result=result, metadata=metadata)
    except QuantValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover – safety net
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc


def _dispatch(req: AnalysisRequest) -> tuple[dict, dict]:
    m = req.method

    if m == "returns":
        prices = _require(req.prices, "prices")
        rets = returns_from_prices(prices, method=req.returns_method)
        if req.returns_method == "simple":
            cum = to_float_list(cumulative_return_series(rets))
            total = cumulative_return(rets)
        else:
            simple = to_float_list(simple_returns(prices))
            cum = to_float_list(cumulative_return_series(simple))
            total = cumulative_return(simple)
        return (
            {
                "returns": rets,
                "returns_method": req.returns_method,
                "cumulative_return_series": cum,
                "total_cumulative_return": total,
            },
            {"observations": len(prices), "return_observations": len(rets)},
        )

    if m == "volatility":
        returns = _get_returns(req)
        metrics = volatility_metrics(returns, annualization_factor=req.annualization_factor)
        return metrics, {"observations": metrics["observations"]}

    if m == "drawdown":
        if req.prices is not None:
            metrics = drawdown_metrics(series=req.prices)
        else:
            returns = _get_returns(req)
            metrics = drawdown_metrics(returns=returns)
        return metrics, {"observations": metrics["observations"]}

    if m == "var":
        returns = _get_returns(req)
        var = historical_var(returns, confidence=req.confidence)
        return (
            {"var": var, "confidence": req.confidence, "convention": "positive_loss"},
            {"observations": len(returns)},
        )

    if m == "cvar":
        returns = _get_returns(req)
        cvar = historical_cvar(returns, confidence=req.confidence)
        return (
            {"cvar": cvar, "confidence": req.confidence, "convention": "positive_loss"},
            {"observations": len(returns)},
        )

    if m == "risk":
        returns = _get_returns(req)
        metrics = risk_metrics(returns, confidence=req.confidence)
        return metrics, {"observations": metrics["observations"]}

    if m == "sharpe":
        returns = _get_returns(req)
        s = sharpe_ratio(
            returns,
            risk_free_rate=req.risk_free_rate,
            annualization_factor=None,
        )
        s_ann = sharpe_ratio(
            returns,
            risk_free_rate=req.risk_free_rate,
            annualization_factor=req.annualization_factor,
        )
        return (
            {
                "sharpe": s,
                "sharpe_annualized": s_ann,
                "risk_free_rate": req.risk_free_rate,
                "annualization_factor": req.annualization_factor,
            },
            {"observations": len(returns)},
        )

    if m == "sortino":
        returns = _get_returns(req)
        s = sortino_ratio(returns, target=req.target, annualization_factor=None)
        s_ann = sortino_ratio(
            returns, target=req.target, annualization_factor=req.annualization_factor
        )
        return (
            {
                "sortino": s,
                "sortino_annualized": s_ann,
                "target": req.target,
                "annualization_factor": req.annualization_factor,
            },
            {"observations": len(returns)},
        )

    if m == "performance":
        returns = _get_returns(req)
        metrics = performance_metrics(
            returns,
            risk_free_rate=req.risk_free_rate,
            target=req.target,
            annualization_factor=req.annualization_factor,
        )
        return metrics, {"observations": metrics["observations"]}

    if m == "correlation":
        a = _require(req.returns_a, "returns_a")
        b = _require(req.returns_b, "returns_b")
        corr = pearson_correlation(a, b)
        return {"correlation": corr}, {"observations": min(len(a), len(b))}

    if m == "covariance":
        a = _require(req.returns_a, "returns_a")
        b = _require(req.returns_b, "returns_b")
        cov = covariance(a, b)
        return {"covariance": cov, "ddof": 1}, {"observations": min(len(a), len(b))}

    if m == "correlation_matrix":
        data = _require(req.multi_returns, "multi_returns")
        matrix = correlation_matrix(data, labels=req.labels)
        return matrix, {"observations": matrix["observations"]}

    if m == "covariance_matrix":
        data = _require(req.multi_returns, "multi_returns")
        matrix = covariance_matrix(data, labels=req.labels)
        return matrix, {"observations": matrix["observations"]}

    if m == "beta":
        asset = _require(req.asset_returns or req.returns_a, "asset_returns")
        bench = _require(req.benchmark_returns or req.returns_b, "benchmark_returns")
        metrics = beta_metrics(asset, bench)
        return metrics, {"observations": metrics["observations"]}

    if m == "monte_carlo":
        result = simulate_paths(
            initial_value=req.initial_value,
            mu=req.mu,
            sigma=req.sigma,
            returns=req.returns,
            horizon=req.horizon,
            n_simulations=req.n_simulations,
            seed=req.seed,
        )
        return result, {
            "n_simulations": result["n_simulations"],
            "horizon": result["horizon"],
        }

    if m == "scenario":
        weights = _require(req.weights, "weights")
        shocks = _require(req.shocks, "shocks")
        result = portfolio_scenario(weights, shocks, labels=req.labels)
        return result, {"n_assets": result["n_assets"]}

    if m == "backtest":
        strat = _require(req.strategy_returns or req.returns, "strategy_returns")
        result = run_backtest(
            strategy_returns=strat,
            benchmark_returns=req.benchmark_returns,
            risk_free_rate=req.risk_free_rate,
            annualization_factor=req.annualization_factor,
        )
        return result, {"observations": result["strategy"]["observations"]}

    raise QuantValidationError(f"Unknown method: {m}")


def _get_returns(req: AnalysisRequest) -> list[float]:
    """Obtain returns either directly or from prices."""
    if req.returns is not None:
        return req.returns
    if req.prices is not None:
        return returns_from_prices(req.prices, method=req.returns_method)
    raise QuantValidationError("Either 'returns' or 'prices' must be provided")
