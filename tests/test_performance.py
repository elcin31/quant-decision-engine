"""Tests for Sharpe and Sortino."""

import numpy as np
import pytest

from app.quant.performance import performance_metrics, sharpe_ratio, sortino_ratio
from app.quant.utils import QuantValidationError


def test_sharpe_zero_rf():
    r = [0.01, 0.02, -0.005, 0.015]
    s = sharpe_ratio(r, risk_free_rate=0.0)
    expected = float(np.mean(r) / np.std(r, ddof=1))
    assert abs(s - expected) < 1e-12


def test_sharpe_annualized():
    r = [0.01, 0.02, -0.005, 0.015]
    s = sharpe_ratio(r, risk_free_rate=0.0, annualization_factor=252)
    s_period = sharpe_ratio(r, risk_free_rate=0.0)
    assert abs(s - s_period * np.sqrt(252)) < 1e-10


def test_sharpe_zero_vol():
    assert sharpe_ratio([0.01, 0.01, 0.01], risk_free_rate=0.0) is None


def test_sortino_no_downside():
    r = [0.01, 0.02, 0.015]
    assert sortino_ratio(r, target=0.0) is None


def test_sortino_known():
    r = [0.05, -0.02, 0.03, -0.01]
    s = sortino_ratio(r, target=0.0)
    assert s is not None
    assert s > 0


def test_performance_metrics():
    r = [0.01, -0.02, 0.015, 0.005, -0.01]
    m = performance_metrics(r)
    assert "sharpe" in m and "sortino" in m
    assert m["observations"] == 5


def test_insufficient():
    with pytest.raises(QuantValidationError):
        sharpe_ratio([0.01])
