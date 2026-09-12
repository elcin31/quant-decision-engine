"""Drawdown calculations.

Conventions
-----------
- Running maximum: cumulative maximum of the equity curve (or price series).
- Drawdown at t: (value_t / running_max_t) - 1  (always <= 0).
- Maximum drawdown: most negative drawdown (scalar, <= 0).
- Drawdown duration: number of periods from peak to trough for the max drawdown,
  and optionally time under water for the whole series.

We work on a wealth / price index series (positive). If returns are supplied,
they are first converted to a cumulative wealth series starting at 1.0.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.utils import QuantValidationError, to_float_list, to_python_scalar, validate_series


def _wealth_from_returns(returns: np.ndarray) -> np.ndarray:
    """Convert simple returns to wealth series starting at 1.0."""
    if (returns <= -1.0).any():
        raise QuantValidationError("returns contain values <= -1")
    return np.cumprod(1.0 + returns)


def running_maximum(series: Sequence[float] | np.ndarray) -> np.ndarray:
    """Cumulative maximum of a positive series."""
    s = validate_series(series, name="series", min_length=1, positive=True)
    return np.maximum.accumulate(s)


def drawdown_series(
    series: Sequence[float] | np.ndarray | None = None,
    returns: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """
    Compute drawdown series (values <= 0).

    Provide either a price/wealth `series` or `returns` (simple).
    """
    if series is not None:
        s = validate_series(series, name="series", min_length=1, positive=True)
    elif returns is not None:
        r = validate_series(returns, name="returns", min_length=1)
        s = _wealth_from_returns(r)
    else:
        raise QuantValidationError("Provide either series or returns")

    peak = np.maximum.accumulate(s)
    dd = (s / peak) - 1.0
    return dd


def maximum_drawdown(
    series: Sequence[float] | np.ndarray | None = None,
    returns: Sequence[float] | np.ndarray | None = None,
) -> float:
    """
    Maximum drawdown (most negative value of the drawdown series).

    Returns a number <= 0. Example: -0.25 means a 25% peak-to-trough decline.
    """
    dd = drawdown_series(series=series, returns=returns)
    return float(np.min(dd))


def drawdown_duration(
    series: Sequence[float] | np.ndarray | None = None,
    returns: Sequence[float] | np.ndarray | None = None,
) -> dict[str, int | float | None]:
    """
    Compute maximum drawdown duration metrics.

    Returns
    -------
    dict with:
      - max_drawdown: float (<= 0)
      - peak_index: int (index of the peak before max DD)
      - trough_index: int (index of the trough)
      - duration_periods: int (trough_index - peak_index)
      - recovery_index: int | None (first index after trough that recovers to peak, or None)
      - underwater_periods: int (total periods where drawdown < 0)
    """
    if series is not None:
        s = validate_series(series, name="series", min_length=1, positive=True)
    elif returns is not None:
        r = validate_series(returns, name="returns", min_length=1)
        s = _wealth_from_returns(r)
    else:
        raise QuantValidationError("Provide either series or returns")

    dd = drawdown_series(series=s)
    max_dd = float(np.min(dd))
    trough_idx = int(np.argmin(dd))

    peak = np.maximum.accumulate(s)
    peak_val = peak[trough_idx]
    peak_candidates = np.where(s[: trough_idx + 1] == peak_val)[0]
    peak_idx = int(peak_candidates[-1]) if len(peak_candidates) else 0

    duration = trough_idx - peak_idx

    recovery_idx = None
    if trough_idx + 1 < s.size:
        recovered = np.where(s[trough_idx + 1 :] >= peak_val)[0]
        if len(recovered):
            recovery_idx = int(trough_idx + 1 + recovered[0])

    underwater = int(np.sum(dd < 0))

    return {
        "max_drawdown": to_python_scalar(max_dd),
        "peak_index": peak_idx,
        "trough_index": trough_idx,
        "duration_periods": duration,
        "recovery_index": recovery_idx,
        "underwater_periods": underwater,
    }


def drawdown_metrics(
    series: Sequence[float] | np.ndarray | None = None,
    returns: Sequence[float] | np.ndarray | None = None,
) -> dict:
    """
    Full drawdown analysis suitable for API response.
    """
    dd = drawdown_series(series=series, returns=returns)
    duration_info = drawdown_duration(series=series, returns=returns)
    return {
        "max_drawdown": duration_info["max_drawdown"],
        "drawdown_series": to_float_list(dd),
        "peak_index": duration_info["peak_index"],
        "trough_index": duration_info["trough_index"],
        "duration_periods": duration_info["duration_periods"],
        "recovery_index": duration_info["recovery_index"],
        "underwater_periods": duration_info["underwater_periods"],
        "observations": int(dd.size),
    }
