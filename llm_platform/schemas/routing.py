"""Routing schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from llm_platform.schemas.enums import Capability


class RouteRequest(BaseModel):
    """Routing request used by capability-based selection."""

    capability: Capability | str
    labels: dict[str, str] = Field(default_factory=dict)
    preferred_model_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RouteDecision(BaseModel):
    model_id: str
    deployment_id: str
    endpoint: str
    capability: Capability | str
    reason: str
    requires_cold_start: bool = False
