"""Risk metrics: Historical VaR and CVaR (Expected Shortfall).

Sign convention (consistent across the project)
-----------------------------------------------
VaR and CVaR are reported as **positive numbers representing potential loss**.

Example:
  If the 5% quantile of the return distribution is -0.03,
  then VaR(95%) = 0.03  (a 3% loss).

CVaR is the expected loss given that returns are at or below the VaR threshold,
also expressed as a positive number.

Historical method only (no parametric or Monte-Carlo VaR in this module).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.config import MIN_OBSERVATIONS, SUPPORTED_CONFIDENCE_LEVELS
from app.quant.utils import QuantValidationError, to_python_scalar, validate_confidence, validate_series


def historical_var(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
) -> float:
    conf = validate_confidence(confidence)
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    alpha = 1.0 - conf
    quantile = float(np.quantile(r, alpha))
    var = max(-quantile, 0.0)
    return var


def historical_cvar(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
) -> float:
    conf = validate_confidence(confidence)
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    alpha = 1.0 - conf
    threshold = float(np.quantile(r, alpha))
    tail = r[r <= threshold]
    if tail.size == 0:
        return max(-threshold, 0.0)
    es = -float(np.mean(tail))
    return max(es, 0.0)


def risk_metrics(
    returns: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
) -> dict:
    conf = validate_confidence(confidence)
    r = validate_series(returns, name="returns", min_length=MIN_OBSERVATIONS)
    var = historical_var(r, conf)
    cvar = historical_cvar(r, conf)
    return {
        "var": to_python_scalar(var),
        "cvar": to_python_scalar(cvar),
        "confidence": conf,
        "observations": int(r.size),
        "convention": "positive_loss",
    }
