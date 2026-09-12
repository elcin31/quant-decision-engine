"""Tests for volatility module."""

import numpy as np
import pytest

from app.quant.volatility import annualized_volatility, daily_volatility, volatility_metrics
from app.quant.utils import QuantValidationError


def test_daily_vol_known():
    r = [0.01, -0.01, 0.01, -0.01]
    vol = daily_volatility(r)
    expected = float(np.std(r, ddof=1))
    assert abs(vol - expected) < 1e-12


def test_constant_returns_zero_vol():
    assert daily_volatility([0.01, 0.01, 0.01]) == 0.0


def test_annualized():
    r = [0.01, -0.01, 0.01, -0.01]
    daily = daily_volatility(r)
    ann = annualized_volatility(r, annualization_factor=252)
    assert abs(ann - daily * np.sqrt(252)) < 1e-12


def test_metrics():
    r = [0.01, 0.02, -0.01, 0.005]
    m = volatility_metrics(r)
    assert "daily" in m and "annualized" in m
    assert m["observations"] == 4
    assert m["annualization_factor"] == 252


def test_insufficient():
    with pytest.raises(QuantValidationError):
        daily_volatility([0.01])


def test_invalid_ann_factor():
    with pytest.raises(QuantValidationError):
        annualized_volatility([0.01, 0.02], annualization_factor=0)
