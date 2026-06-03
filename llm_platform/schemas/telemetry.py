"""Telemetry schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    request_id: str
    deployment_id: str
    model_name: str
    latency_ms: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit: bool = False
    error: str | None = None
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricsSnapshot(BaseModel):
    total_requests: int = 0
    total_errors: int = 0
    average_latency_ms: float = 0.0
