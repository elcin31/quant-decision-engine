"""Tests for VaR / CVaR."""

import numpy as np
import pytest

from app.quant.risk import historical_cvar, historical_var, risk_metrics
from app.quant.utils import QuantValidationError


def test_var_positive_loss_convention():
    r = np.array([-0.05, -0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04])
    var95 = historical_var(r, confidence=0.90)
    assert var95 > 0


def test_var_known_distribution():
    r = np.linspace(-0.10, 0.10, 100)
    var = historical_var(r, confidence=0.95)
    assert 0.08 < var < 0.11


def test_cvar_ge_var():
    rng = np.random.default_rng(42)
    r = rng.normal(0, 0.02, 1000)
    var = historical_var(r, 0.95)
    cvar = historical_cvar(r, 0.95)
    assert cvar >= var - 1e-12


def test_risk_metrics():
    r = [0.01, -0.02, 0.015, -0.03, 0.005, -0.01]
    m = risk_metrics(r, confidence=0.95)
    assert "var" in m and "cvar" in m
    assert m["convention"] == "positive_loss"


def test_invalid_confidence():
    with pytest.raises(QuantValidationError):
        historical_var([0.01, -0.01], confidence=1.5)


def test_insufficient():
    with pytest.raises(QuantValidationError):
        historical_var([0.01])
