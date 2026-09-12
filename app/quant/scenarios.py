"""Deterministic scenario analysis.

This module applies user-defined shocks to assets and computes
portfolio-level impact. It is purely deterministic – no probabilities.
"""

from __future__ import annotations

from typing import Sequence

from app.quant.utils import QuantValidationError, to_python_scalar


def single_asset_impact(weight: float, shock: float) -> float:
    if not isinstance(weight, (int, float)) or not isinstance(shock, (int, float)):
        raise QuantValidationError("weight and shock must be numeric")
    return float(weight) * float(shock)


def portfolio_scenario(
    weights: Sequence[float],
    shocks: Sequence[float],
    labels: Sequence[str] | None = None,
) -> dict:
    w = list(weights)
    s = list(shocks)
    if len(w) != len(s):
        raise QuantValidationError(
            f"weights and shocks length mismatch: {len(w)} vs {len(s)}"
        )
    if len(w) == 0:
        raise QuantValidationError("weights/shocks cannot be empty")

    if labels is not None and len(labels) != len(w):
        raise QuantValidationError("labels length must match weights")

    labels_out = list(labels) if labels is not None else [f"asset_{i}" for i in range(len(w))]

    contributions = []
    total = 0.0
    for i, (wi, si) in enumerate(zip(w, s)):
        if not isinstance(wi, (int, float)) or not isinstance(si, (int, float)):
            raise QuantValidationError(f"Non-numeric weight or shock at index {i}")
        contrib = float(wi) * float(si)
        total += contrib
        contributions.append(
            {
                "label": labels_out[i],
                "weight": float(wi),
                "shock": float(si),
                "contribution": to_python_scalar(contrib),
            }
        )

    return {
        "contributions": contributions,
        "total_impact": to_python_scalar(total),
        "n_assets": len(w),
        "assumption": "Deterministic shocks applied linearly; no rebalancing or second-order effects.",
        "note": "This is scenario analysis, not a probability-weighted forecast.",
    }
