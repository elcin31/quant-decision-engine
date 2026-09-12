"""Return calculations.

Conventions
-----------
- Simple returns: r_t = (P_t - P_{t-1}) / P_{t-1}
- Log returns:    r_t = ln(P_t / P_{t-1})
- Cumulative return (scalar): product of (1 + simple returns) - 1
- Cumulative return series: running product of (1 + simple returns) - 1

Assumptions
-----------
- Prices must be strictly positive.
- Missing / zero / negative prices raise QuantValidationError.
- Returns are computed on consecutive observations after validation.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.utils import QuantValidationError, to_float_list, validate_series


def simple_returns(prices: Sequence[float] | np.ndarray) -> np.ndarray:
    """
    Compute simple (arithmetic) returns from a price series.

    Parameters
    ----------
    prices : array-like
        Strictly positive price series ordered by time.

    Returns
    -------
    np.ndarray
        Simple returns of length len(prices) - 1.
    """
    p = validate_series(prices, name="prices", min_length=2, positive=True)
    return (p[1:] - p[:-1]) / p[:-1]


def log_returns(prices: Sequence[float] | np.ndarray) -> np.ndarray:
    """
    Compute logarithmic returns from a price series.

    Parameters
    ----------
    prices : array-like
        Strictly positive price series ordered by time.

    Returns
    -------
    np.ndarray
        Log returns of length len(prices) - 1.
    """
    p = validate_series(prices, name="prices", min_length=2, positive=True)
    return np.log(p[1:] / p[:-1])


def cumulative_return(returns: Sequence[float] | np.ndarray) -> float:
    """
    Compute the total cumulative simple return over the series.

    Parameters
    ----------
    returns : array-like
        Simple returns (not log returns).

    Returns
    -------
    float
        (product of (1 + r_i)) - 1
    """
    r = validate_series(returns, name="returns", min_length=1, allow_nan=False)
    if (r <= -1.0).any():
        raise QuantValidationError(
            "returns contain values <= -1; cumulative product would be non-positive"
        )
    return float(np.prod(1.0 + r) - 1.0)


def cumulative_return_series(returns: Sequence[float] | np.ndarray) -> np.ndarray:
    """
    Compute the running cumulative simple return series.

    Parameters
    ----------
    returns : array-like
        Simple returns (not log returns).

    Returns
    -------
    np.ndarray
        Cumulative return at each step: (cumprod(1+r) - 1)
    """
    r = validate_series(returns, name="returns", min_length=1, allow_nan=False)
    if (r <= -1.0).any():
        raise QuantValidationError(
            "returns contain values <= -1; cumulative product would be non-positive"
        )
    return np.cumprod(1.0 + r) - 1.0


def returns_from_prices(
    prices: Sequence[float] | np.ndarray,
    method: str = "simple",
) -> list[float]:
    """
    Convenience wrapper returning JSON-serializable list of returns.

    Parameters
    ----------
    prices : array-like
        Price series.
    method : {"simple", "log"}
        Return type.

    Returns
    -------
    list[float]
    """
    method = method.lower().strip()
    if method == "simple":
        r = simple_returns(prices)
    elif method == "log":
        r = log_returns(prices)
    else:
        raise QuantValidationError(f"Unknown return method: {method!r}. Use 'simple' or 'log'.")
    return to_float_list(r)
