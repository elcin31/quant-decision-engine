"""Utility helpers for input validation and JSON serialization."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd


class QuantValidationError(ValueError):
    """Domain-specific validation error for quantitative inputs."""

    pass


def to_float_list(arr: np.ndarray | pd.Series | Sequence[float]) -> list[float]:
    """Convert array-like to a plain list of Python floats (JSON-safe)."""
    if isinstance(arr, pd.Series):
        arr = arr.to_numpy(dtype=float)
    elif not isinstance(arr, np.ndarray):
        arr = np.asarray(arr, dtype=float)
    return [float(x) if np.isfinite(x) else None for x in arr]  # type: ignore[misc]


def to_python_scalar(x: Any) -> float | int | None:
    """Convert NumPy scalar to native Python type."""
    if x is None:
        return None
    if isinstance(x, (np.floating, float)):
        val = float(x)
        return val if np.isfinite(val) else None
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    return x


def validate_series(
    data: Sequence[float] | np.ndarray | pd.Series,
    name: str = "series",
    min_length: int = 1,
    allow_nan: bool = False,
    positive: bool = False,
) -> np.ndarray:
    """
    Validate and convert input to a 1-D float NumPy array.

    Raises QuantValidationError on invalid input.
    """
    if data is None:
        raise QuantValidationError(f"{name} cannot be None")

    try:
        arr = np.asarray(data, dtype=float).ravel()
    except (TypeError, ValueError) as exc:
        raise QuantValidationError(f"{name} must be convertible to float array: {exc}") from exc

    if arr.size == 0:
        raise QuantValidationError(f"{name} is empty")

    if arr.size < min_length:
        raise QuantValidationError(
            f"{name} requires at least {min_length} observations, got {arr.size}"
        )

    if not allow_nan and (np.isnan(arr).any() or np.isinf(arr).any()):
        raise QuantValidationError(f"{name} contains NaN or infinite values")

    if positive and (arr <= 0).any():
        raise QuantValidationError(f"{name} must contain strictly positive values")

    return arr


def validate_confidence(confidence: float) -> float:
    """Validate VaR/CVaR confidence level."""
    if not isinstance(confidence, (int, float)):
        raise QuantValidationError("confidence must be a number")
    conf = float(confidence)
    if not 0.0 < conf < 1.0:
        raise QuantValidationError(f"confidence must be in (0, 1), got {conf}")
    return conf


def align_series(
    a: np.ndarray | pd.Series,
    b: np.ndarray | pd.Series,
    name_a: str = "series_a",
    name_b: str = "series_b",
) -> tuple[np.ndarray, np.ndarray]:
    """
    Align two series by dropping NaNs pairwise.
    If both are plain arrays of equal length, returns them as-is after validation.
    """
    if isinstance(a, pd.Series) and isinstance(b, pd.Series):
        combined = pd.concat([a, b], axis=1).dropna()
        if combined.empty or len(combined) < 2:
            raise QuantValidationError(
                f"Insufficient overlapping observations between {name_a} and {name_b}"
            )
        return combined.iloc[:, 0].to_numpy(dtype=float), combined.iloc[:, 1].to_numpy(dtype=float)

    arr_a = validate_series(a, name_a, min_length=2)
    arr_b = validate_series(b, name_b, min_length=2)
    if arr_a.size != arr_b.size:
        raise QuantValidationError(
            f"{name_a} and {name_b} length mismatch: {arr_a.size} vs {arr_b.size}"
        )
    mask = np.isfinite(arr_a) & np.isfinite(arr_b)
    if mask.sum() < 2:
        raise QuantValidationError(
            f"Insufficient finite overlapping observations between {name_a} and {name_b}"
        )
    return arr_a[mask], arr_b[mask]
