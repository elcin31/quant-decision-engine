"""Tests for drawdown module."""

import numpy as np
import pytest

from app.quant.drawdown import (
    drawdown_metrics,
    drawdown_series,
    maximum_drawdown,
    running_maximum,
)
from app.quant.utils import QuantValidationError


def test_running_max():
    s = [100.0, 110.0, 105.0, 120.0]
    rm = running_maximum(s)
    np.testing.assert_allclose(rm, [100, 110, 110, 120])


def test_drawdown_series():
    s = [100.0, 90.0, 95.0]
    dd = drawdown_series(series=s)
    np.testing.assert_allclose(dd, [0.0, -0.10, -0.05], rtol=1e-10)


def test_max_drawdown():
    s = [100.0, 120.0, 90.0, 95.0]
    assert abs(maximum_drawdown(series=s) - (-0.25)) < 1e-12


def test_from_returns():
    r = [0.10, -0.20, 0.05]
    dd = drawdown_series(returns=r)
    assert maximum_drawdown(returns=r) <= 0


def test_metrics():
    s = [100.0, 110.0, 80.0, 90.0, 120.0]
    m = drawdown_metrics(series=s)
    assert m["max_drawdown"] == pytest.approx(-30 / 110, rel=1e-10)
    assert len(m["drawdown_series"]) == 5
    assert m["trough_index"] == 2


def test_empty():
    with pytest.raises(QuantValidationError):
        drawdown_series(series=[])
