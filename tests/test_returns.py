"""Tests for returns module."""

import numpy as np
import pytest

from app.quant.returns import (
    cumulative_return,
    cumulative_return_series,
    log_returns,
    returns_from_prices,
    simple_returns,
)
from app.quant.utils import QuantValidationError


def test_simple_returns_known():
    prices = [100.0, 110.0, 99.0]
    r = simple_returns(prices)
    np.testing.assert_allclose(r, [0.10, -0.10], rtol=1e-10)


def test_log_returns_known():
    prices = [100.0, 110.0]
    r = log_returns(prices)
    expected = np.log(1.1)
    np.testing.assert_allclose(r, [expected], rtol=1e-10)


def test_cumulative_return():
    r = [0.10, -0.10]
    assert abs(cumulative_return(r) - (-0.01)) < 1e-12


def test_cumulative_return_series():
    r = [0.10, 0.05]
    series = cumulative_return_series(r)
    np.testing.assert_allclose(series, [0.10, 0.155], rtol=1e-10)


def test_empty_prices():
    with pytest.raises(QuantValidationError):
        simple_returns([])


def test_single_price():
    with pytest.raises(QuantValidationError):
        simple_returns([100.0])


def test_zero_price():
    with pytest.raises(QuantValidationError):
        simple_returns([100.0, 0.0])


def test_negative_price():
    with pytest.raises(QuantValidationError):
        simple_returns([100.0, -10.0])


def test_returns_from_prices():
    prices = [100.0, 105.0, 110.0]
    simple = returns_from_prices(prices, method="simple")
    assert len(simple) == 2
    assert abs(simple[0] - 0.05) < 1e-12


def test_invalid_method():
    with pytest.raises(QuantValidationError):
        returns_from_prices([100.0, 110.0], method="foo")


def test_cumulative_with_total_loss():
    with pytest.raises(QuantValidationError):
        cumulative_return([-1.0, 0.1])
