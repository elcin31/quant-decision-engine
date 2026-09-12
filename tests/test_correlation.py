"""Tests for correlation and covariance."""

import numpy as np
import pytest

from app.quant.correlation import (
    correlation_matrix,
    covariance,
    covariance_matrix,
    pearson_correlation,
)
from app.quant.utils import QuantValidationError


def test_perfect_correlation():
    a = [1.0, 2.0, 3.0, 4.0]
    b = [2.0, 4.0, 6.0, 8.0]
    assert abs(pearson_correlation(a, b) - 1.0) < 1e-12


def test_perfect_negative():
    a = [1.0, 2.0, 3.0, 4.0]
    b = [4.0, 3.0, 2.0, 1.0]
    assert abs(pearson_correlation(a, b) - (-1.0)) < 1e-12


def test_covariance_known():
    a = [1.0, 2.0, 3.0]
    b = [1.0, 2.0, 3.0]
    cov = covariance(a, b)
    expected = float(np.var(a, ddof=1))
    assert abs(cov - expected) < 1e-12


def test_correlation_matrix():
    data = [
        [0.01, 0.02, -0.01, 0.015],
        [0.005, 0.01, -0.005, 0.008],
    ]
    m = correlation_matrix(data, labels=["A", "B"])
    assert m["labels"] == ["A", "B"]
    assert abs(m["matrix"][0][0] - 1.0) < 1e-10
    assert abs(m["matrix"][1][1] - 1.0) < 1e-10


def test_constant_series():
    with pytest.raises(QuantValidationError):
        pearson_correlation([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])


def test_length_mismatch():
    with pytest.raises(QuantValidationError):
        pearson_correlation([1.0, 2.0], [1.0, 2.0, 3.0])
