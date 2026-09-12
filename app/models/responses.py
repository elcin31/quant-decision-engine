"""Pydantic response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    method: str
    result: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ErrorResponse(BaseModel):
    detail: str
    method: str | None = None
