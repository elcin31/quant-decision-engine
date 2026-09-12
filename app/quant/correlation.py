"""Correlation and covariance calculations.

Conventions
-----------
- Sample correlation / covariance (ddof=1) via NumPy.
- Pearson correlation only.
- Covariance matrix and correlation matrix for multiple series.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from app.quant.config import MIN_OBS_CORRELATION
from app.quant.utils import QuantValidationError, align_series, to_python_scalar, validate_series


def pearson_correlation(
    a: Sequence[float] | np.ndarray,
    b: Sequence[float] | np.ndarray,
) -> float:
    """
    Pearson correlation between two series.

    Raises QuantValidationError if variance of either series is zero
    or if there are insufficient observations.
    """
    x, y = align_series(a, b, "series_a", "series_b")
    if x.size < MIN_OBS_CORRELATION:
        raise QuantValidationError(
            f"Need at least {MIN_OBS_CORRELATION} observations for correlation, got {x.size}"
        )
    if np.allclose(x, x[0]) or np.allclose(y, y[0]):
        raise QuantValidationError(
            "Cannot compute correlation: one or both series are constant"
        )
    corr = float(np.corrcoef(x, y)[0, 1])
    if not np.isfinite(corr):
        raise QuantValidationError("Correlation computation produced non-finite result")
    return corr


def covariance(
    a: Sequence[float] | np.ndarray,
    b: Sequence[float] | np.ndarray,
) -> float:
    """
    Sample covariance (ddof=1) between two series.
    """
    x, y = align_series(a, b, "series_a", "series_b")
    if x.size < 2:
        raise QuantValidationError("Need at least 2 observations for covariance")
    cov = float(np.cov(x, y, ddof=1)[0, 1])
    return cov


def correlation_matrix(
    data: Sequence[Sequence[float]] | np.ndarray,
    labels: Sequence[str] | None = None,
) -> dict:
    """
    Compute Pearson correlation matrix for multiple series.

    Parameters
    ----------
    data : array-like of shape (n_assets, n_obs) or (n_obs, n_assets)
           Prefer (n_assets, n_obs). If 2-D, we treat rows as assets.
    labels : optional list of asset names.

    Returns
    -------
    dict with matrix (list of lists), labels, observations.
    """
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise QuantValidationError("data must be 2-dimensional")
    n_assets, n_obs = arr.shape
    if n_obs < MIN_OBS_CORRELATION:
        # Try transposed interpretation
        if arr.shape[0] >= MIN_OBS_CORRELATION and arr.shape[1] >= 2:
            arr = arr.T
            n_assets, n_obs = arr.shape
        else:
            raise QuantValidationError(
                f"Insufficient observations for correlation matrix (need >= {MIN_OBS_CORRELATION})"
            )

    if labels is not None and len(labels) != n_assets:
        raise QuantValidationError("labels length must match number of assets")

    # Drop columns with any NaN
    mask = np.all(np.isfinite(arr), axis=0)
    arr = arr[:, mask]
    if arr.shape[1] < MIN_OBS_CORRELATION:
        raise QuantValidationError("Insufficient finite observations after cleaning")

    # Check for constant series
    for i in range(n_assets):
        if np.allclose(arr[i], arr[i, 0]):
            raise QuantValidationError(f"Asset index {i} is constant; correlation undefined")

    corr = np.corrcoef(arr)
    if not np.all(np.isfinite(corr)):
        raise QuantValidationError("Correlation matrix contains non-finite values")

    labels_out = list(labels) if labels is not None else [f"asset_{i}" for i in range(n_assets)]
    matrix = [[to_python_scalar(corr[i, j]) for j in range(n_assets)] for i in range(n_assets)]

    return {
        "matrix": matrix,
        "labels": labels_out,
        "observations": int(arr.shape[1]),
    }


def covariance_matrix(
    data: Sequence[Sequence[float]] | np.ndarray,
    labels: Sequence[str] | None = None,
) -> dict:
    """
    Sample covariance matrix (ddof=1). Same layout conventions as correlation_matrix.
    """
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise QuantValidationError("data must be 2-dimensional")
    n_assets, n_obs = arr.shape
    if n_obs < 2:
        if arr.shape[0] >= 2 and arr.shape[1] >= 2:
            arr = arr.T
            n_assets, n_obs = arr.shape
        else:
            raise QuantValidationError("Insufficient observations for covariance matrix")

    if labels is not None and len(labels) != n_assets:
        raise QuantValidationError("labels length must match number of assets")

    mask = np.all(np.isfinite(arr), axis=0)
    arr = arr[:, mask]
    if arr.shape[1] < 2:
        raise QuantValidationError("Insufficient finite observations after cleaning")

    cov = np.cov(arr, ddof=1)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    if not np.all(np.isfinite(cov)):
        raise QuantValidationError("Covariance matrix contains non-finite values")

    labels_out = list(labels) if labels is not None else [f"asset_{i}" for i in range(n_assets)]
    matrix = [[to_python_scalar(cov[i, j]) for j in range(n_assets)] for i in range(n_assets)]

    return {
        "matrix": matrix,
        "labels": labels_out,
        "observations": int(arr.shape[1]),
        "ddof": 1,
    }
