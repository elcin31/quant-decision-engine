"""Shared configuration and constants for the quantitative engine."""

DEFAULT_ANNUALIZATION_FACTOR: int = 252
DEFAULT_MONTE_CARLO_SIMULATIONS: int = 10_000
DEFAULT_MONTE_CARLO_HORIZON: int = 252
SUPPORTED_CONFIDENCE_LEVELS: tuple[float, ...] = (0.90, 0.95, 0.99)
MIN_OBSERVATIONS: int = 2
MIN_OBS_CORRELATION: int = 3
