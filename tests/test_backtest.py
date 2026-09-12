"""Tests for backtest engine."""

import numpy as np
import pytest

from app.quant.backtest import cagr, run_backtest
from app.quant.utils import QuantValidationError


def test_cagr_known():
    r = [0.10, 0.10]
    val = cagr(r, periods_per_year=1)
    expected = (1.21) ** 0.5 - 1
    assert abs(val - expected) < 1e-10


def test_backtest_basic():
    r = [0.01, -0.005, 0.02, 0.0, 0.015]
    result = run_backtest(r, annualization_factor=252)
    assert "strategy" in result
    assert result["strategy"]["observations"] == 5
    assert result["strategy"]["max_drawdown"] <= 0
    assert len(result["strategy"]["cumulative_return_series"]) == 5


def test_backtest_with_benchmark():
    strat = [0.01, 0.02, -0.01, 0.015]
    bench = [0.005, 0.01, -0.005, 0.008]
    result = run_backtest(strat, benchmark_returns=bench)
    assert "benchmark" in result
    assert "relative" in result


def test_length_mismatch():
    with pytest.raises(QuantValidationError):
        run_backtest([0.01, 0.02], benchmark_returns=[0.01])


def test_insufficient():
    with pytest.raises(QuantValidationError):
        run_backtest([0.01])
