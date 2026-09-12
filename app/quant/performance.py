"""Performance ratios: Sharpe and Sortino.

Conventions
-----------
Sharpe ratio
  excess = mean(returns) - risk_free_rate_per_period
  sharpe = excess / std(returns, ddof=1)
  annualized_sharpe = sharpe * sqrt(annualization_factor)

  risk_free_rate is expressed in the **same frequency** as the returns
  (e.g. daily risk-free rate if returns are daily).
  Caller is responsible for converting an annual risk-free rate if needed.

Sortino ratio
  downside deviation = sqrt( mean( min(r - target, 0)^2 ) )   (population style over all obs)
  sortino = (mean(r) - target) / downside_deviation
  annualized similarly.

  If downside_deviation == 0:
    - if excess return >= 0 → +inf (represented as None with a flag, or a large number)
    - if excess return < 0  → -inf
  We return None for infinite cases and set a flag.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.config import DEFAULT_ANNUALIZATION_FACTOR, MIN_OBSERVATIONS
from app.quant.utils import QuantValidationError, to_python_scalar, validate_series


def sharpe_ratio(
    returns: Sequence[float] | np.ndarray,
    risk_free_rate: float = 0.0,
    annualization_factor: int | None = None,
) -> float | None:
    """
    Compute Sharpe ratio.

    Parameters
    ----------
    returns : array-like
        Period returns.
    risk_free_rate : float
        Risk-free rate **per period** (same frequency as returns). Default 0.0.
    annualization_factor : int | None
        If provided, returns the annualized Sharpe.
        If None, returns the per-period Sharpe.

    Returns
    -------
    float | None
        Sharpe ratio, or None if volatility is zero and excess is zero.
    """
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    excess = float(np.mean(r) - risk_free_rate)
    vol = float(np.std(r, ddof=1))

    if vol == 0.0:
        if excess == 0.0:
            return 0.0
        # Infinite Sharpe – return None to avoid non-JSON-serializable inf
        return None

    sharpe = excess / vol
    if annualization_factor is not None:
        if annualization_factor <= 0:
            raise QuantValidationError("annualization_factor must be positive")
        sharpe *= float(np.sqrt(annualization_factor))
    return float(sharpe)


def sortino_ratio(
    returns: Sequence[float] | np.ndarray,
    target: float = 0.0,
    annualization_factor: int | None = None,
) -> float | None:
    """
    Compute Sortino ratio.

    Downside deviation is defined as:
        sqrt( mean( min(r_i - target, 0)^2 ) )
    over all observations (not only the downside ones).

    Parameters
    ----------
    returns : array-like
        Period returns.
    target : float
        Target / minimum acceptable return per period.
    annualization_factor : int | None
        If provided, annualizes the ratio.

    Returns
    -------
    float | None
        Sortino ratio, or None when downside deviation is zero
        (infinite case).
    """
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    excess = float(np.mean(r) - target)
    downside = np.minimum(r - target, 0.0)
    downside_dev = float(np.sqrt(np.mean(downside ** 2)))

    if downside_dev == 0.0:
        # No downside observations
        if excess >= 0.0:
            return None  # +inf
        return None  # -inf also represented as None; caller can inspect excess

    sortino = excess / downside_dev
    if annualization_factor is not None:
        if annualization_factor <= 0:
            raise QuantValidationError("annualization_factor must be positive")
        sortino *= float(np.sqrt(annualization_factor))
    return float(sortino)


def performance_metrics(
    returns: Sequence[float] | np.ndarray,
    risk_free_rate: float = 0.0,
    target: float = 0.0,
    annualization_factor: int = DEFAULT_ANNUALIZATION_FACTOR,
) -> dict:
    """
    Compute Sharpe and Sortino (both per-period and annualized).
    """
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    if annualization_factor <= 0:
        raise QuantValidationError("annualization_factor must be positive")

    sharpe = sharpe_ratio(r, risk_free_rate=risk_free_rate, annualization_factor=None)
    sharpe_ann = sharpe_ratio(r, risk_free_rate=risk_free_rate, annualization_factor=annualization_factor)
    sortino = sortino_ratio(r, target=target, annualization_factor=None)
    sortino_ann = sortino_ratio(r, target=target, annualization_factor=annualization_factor)

    return {
        "sharpe": to_python_scalar(sharpe),
        "sharpe_annualized": to_python_scalar(sharpe_ann),
        "sortino": to_python_scalar(sortino),
        "sortino_annualized": to_python_scalar(sortino_ann),
        "mean_return": to_python_scalar(float(np.mean(r))),
        "risk_free_rate": float(risk_free_rate),
        "target": float(target),
        "annualization_factor": int(annualization_factor),
        "observations": int(r.size),
        "note": "None values indicate zero volatility / zero downside deviation (infinite ratio)",
    }
