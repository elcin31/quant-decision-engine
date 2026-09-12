"""Tests for beta."""

import numpy as np
import pytest

from app.quant.beta import beta, beta_metrics
from app.quant.utils import QuantValidationError


def test_beta_one():
    r = [0.01, -0.02, 0.015, 0.005, -0.01]
    assert abs(beta(r, r) - 1.0) < 1e-10


def test_beta_zero():
    rng = np.random.default_rng(0)
    bench = rng.normal(0, 0.01, 200)
    asset = rng.normal(0, 0.01, 200)
    b = beta(asset, bench)
    assert abs(b) < 0.3


def test_zero_benchmark_var():
    with pytest.raises(QuantValidationError):
        beta([0.01, 0.02, 0.03], [0.0, 0.0, 0.0])


def test_metrics():
    a = [0.01, 0.02, -0.01, 0.015]
    b = [0.005, 0.01, -0.005, 0.008]
    m = beta_metrics(a, b)
    assert "beta" in m
    assert m["observations"] == 4


def test_insufficient():
    with pytest.raises(QuantValidationError):
        beta([0.01], [0.01])
