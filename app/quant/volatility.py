"""Volatility calculations.

Conventions
-----------
- Daily volatility: sample standard deviation of returns (ddof=1).
- Annualized volatility: daily_vol * sqrt(annualization_factor).

Default annualization_factor = 252 (shared config).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.config import DEFAULT_ANNUALIZATION_FACTOR, MIN_OBSERVATIONS
from app.quant.utils import QuantValidationError, to_python_scalar, validate_series


def daily_volatility(returns: Sequence[float] | np.ndarray) -> float:
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    if np.allclose(r, r[0]):
        return 0.0
    return float(np.std(r, ddof=1))


def annualized_volatility(
    returns: Sequence[float] | np.ndarray,
    annualization_factor: int = DEFAULT_ANNUALIZATION_FACTOR,
) -> float:
    if annualization_factor <= 0:
        raise QuantValidationError("annualization_factor must be positive")
    daily = daily_volatility(returns)
    return daily * float(np.sqrt(annualization_factor))


def volatility_metrics(
    returns: Sequence[float] | np.ndarray,
    annualization_factor: int = DEFAULT_ANNUALIZATION_FACTOR,
) -> dict[str, float | int]:
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    daily = daily_volatility(r)
    ann = daily * float(np.sqrt(annualization_factor)) if annualization_factor > 0 else float("nan")
    return {
        "daily": to_python_scalar(daily),
        "annualized": to_python_scalar(ann),
        "observations": int(r.size),
        "annualization_factor": int(annualization_factor),
    }
