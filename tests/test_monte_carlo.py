"""Tests for Monte Carlo simulation."""

import numpy as np
import pytest

from app.quant.monte_carlo import simulate_paths
from app.quant.utils import QuantValidationError


def test_deterministic_seed():
    r1 = simulate_paths(initial_value=100.0, mu=0.001, sigma=0.01, horizon=10, n_simulations=100, seed=42)
    r2 = simulate_paths(initial_value=100.0, mu=0.001, sigma=0.01, horizon=10, n_simulations=100, seed=42)
    assert r1["final_mean"] == r2["final_mean"]
    assert r1["percentiles"]["p50"] == r2["percentiles"]["p50"]


def test_output_structure():
    result = simulate_paths(initial_value=100.0, mu=0.0, sigma=0.02, horizon=5, n_simulations=50, seed=1)
    assert result["n_simulations"] == 50
    assert result["horizon"] == 5
    assert "percentiles" in result
    assert "probability_of_loss" in result
    assert 0.0 <= result["probability_of_loss"] <= 1.0
    assert len(result["sample_paths"]) <= 50
    assert len(result["sample_paths"][0]) == 5


def test_percentile_ordering():
    result = simulate_paths(mu=0.0, sigma=0.02, horizon=20, n_simulations=500, seed=7)
    p = result["percentiles"]
    assert p["p5"] <= p["p10"] <= p["p25"] <= p["p50"] <= p["p75"] <= p["p90"] <= p["p95"]


def test_from_returns():
    returns = [0.01, -0.005, 0.012, 0.003, -0.008]
    result = simulate_paths(returns=returns, horizon=10, n_simulations=100, seed=3)
    assert result["mu"] is not None
    assert result["sigma"] is not None


def test_invalid_initial():
    with pytest.raises(QuantValidationError):
        simulate_paths(initial_value=-1.0, mu=0.0, sigma=0.01)


def test_invalid_n_sim():
    with pytest.raises(QuantValidationError):
        simulate_paths(mu=0.0, sigma=0.01, n_simulations=0)


def test_missing_params():
    with pytest.raises(QuantValidationError):
        simulate_paths(horizon=10)
