"""Monte Carlo price / return path simulation.

Assumptions
-----------
- Geometric Brownian Motion style: each step multiplies by (1 + r)
  where r ~ N(mu, sigma) estimated from historical simple returns,
  OR user-supplied mu / sigma.
- Vectorized with NumPy.
- All outputs are JSON-serializable Python types.

Default: 10_000 paths, 252 steps, seed optional.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.config import (
    DEFAULT_MONTE_CARLO_HORIZON,
    DEFAULT_MONTE_CARLO_SIMULATIONS,
)
from app.quant.utils import QuantValidationError, to_float_list, to_python_scalar, validate_series


def _estimate_params(returns: np.ndarray) -> tuple[float, float]:
    """Estimate mean and std from historical simple returns."""
    mu = float(np.mean(returns))
    sigma = float(np.std(returns, ddof=1)) if returns.size > 1 else 0.0
    return mu, sigma


def simulate_paths(
    initial_value: float = 100.0,
    mu: float | None = None,
    sigma: float | None = None,
    returns: Sequence[float] | np.ndarray | None = None,
    horizon: int = DEFAULT_MONTE_CARLO_HORIZON,
    n_simulations: int = DEFAULT_MONTE_CARLO_SIMULATIONS,
    seed: int | None = None,
) -> dict:
    """
    Run Monte Carlo simulation of price paths.

    Parameters
    ----------
    initial_value : float
        Starting price / wealth (> 0).
    mu, sigma : float | None
        Drift and volatility per period. If None, estimated from `returns`.
    returns : array-like | None
        Historical simple returns used to estimate mu/sigma when not supplied.
    horizon : int
        Number of periods to simulate.
    n_simulations : int
        Number of paths.
    seed : int | None
        Random seed for reproducibility.

    Returns
    -------
    dict
        JSON-serializable results including summary statistics and
        a sample of paths (capped for response size).
    """
    if initial_value <= 0:
        raise QuantValidationError("initial_value must be positive")
    if horizon < 1:
        raise QuantValidationError("horizon must be >= 1")
    if n_simulations < 1:
        raise QuantValidationError("n_simulations must be >= 1")
    if n_simulations > 100_000:
        raise QuantValidationError("n_simulations capped at 100_000 for safety")

    if mu is None or sigma is None:
        if returns is None:
            raise QuantValidationError(
                "Provide either (mu and sigma) or historical returns for estimation"
            )
        r = validate_series(returns, name="returns", min_length=2)
        est_mu, est_sigma = _estimate_params(r)
        mu = mu if mu is not None else est_mu
        sigma = sigma if sigma is not None else est_sigma

    mu = float(mu)
    sigma = float(sigma)
    if sigma < 0:
        raise QuantValidationError("sigma must be non-negative")

    rng = np.random.default_rng(seed)

    # Shape: (n_simulations, horizon)
    shocks = rng.normal(loc=mu, scale=sigma, size=(n_simulations, horizon))
    # Cumulative product of (1 + r)
    # Clip extreme negative returns to avoid non-positive wealth
    factors = 1.0 + shocks
    factors = np.maximum(factors, 1e-12)
    wealth_paths = initial_value * np.cumprod(factors, axis=1)

    # Prepend initial value for full path (optional; we keep final and sample)
    final_values = wealth_paths[:, -1]

    # Statistics
    mean_final = float(np.mean(final_values))
    median_final = float(np.median(final_values))
    std_final = float(np.std(final_values, ddof=1)) if n_simulations > 1 else 0.0

    percentiles = {
        "p5": float(np.percentile(final_values, 5)),
        "p10": float(np.percentile(final_values, 10)),
        "p25": float(np.percentile(final_values, 25)),
        "p50": float(np.percentile(final_values, 50)),
        "p75": float(np.percentile(final_values, 75)),
        "p90": float(np.percentile(final_values, 90)),
        "p95": float(np.percentile(final_values, 95)),
    }

    prob_loss = float(np.mean(final_values < initial_value))
    expected_return = (mean_final / initial_value) - 1.0

    # Sample of paths for visualization (max 50 paths, full horizon)
    max_paths_return = min(50, n_simulations)
    sample_idx = rng.choice(n_simulations, size=max_paths_return, replace=False)
    sample_paths = wealth_paths[sample_idx].tolist()  # list of lists of floats

    # Histogram-friendly final distribution (100 bins)
    hist_counts, hist_edges = np.histogram(final_values, bins=50)
    distribution = {
        "bin_edges": to_float_list(hist_edges),
        "counts": [int(c) for c in hist_counts],
    }

    return {
        "initial_value": float(initial_value),
        "mu": mu,
        "sigma": sigma,
        "horizon": int(horizon),
        "n_simulations": int(n_simulations),
        "seed": seed,
        "final_mean": to_python_scalar(mean_final),
        "final_median": to_python_scalar(median_final),
        "final_std": to_python_scalar(std_final),
        "percentiles": {k: to_python_scalar(v) for k, v in percentiles.items()},
        "probability_of_loss": to_python_scalar(prob_loss),
        "expected_return": to_python_scalar(expected_return),
        "sample_paths": sample_paths,  # list[list[float]]
        "final_distribution": distribution,
        "observations_used_for_params": int(len(returns)) if returns is not None else None,
    }
