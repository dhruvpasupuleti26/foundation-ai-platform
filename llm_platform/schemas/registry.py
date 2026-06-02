"""Registry and deployment schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from llm_platform.schemas.enums import Capability, DeploymentStatus, LifecycleState, ModelStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ModelRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    version: str
    family: str
    engine: str
    capabilities: list[Capability | str] = Field(default_factory=list)
    memory_requirement_gb: int
    ownership: str
    status: ModelStatus = ModelStatus.REGISTERED
    created_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeploymentRecord(BaseModel):
    deployment_id: str = Field(default_factory=lambda: str(uuid4()))
    model_id: str
    endpoint: str
    engine: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    last_used: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LifecycleRecord(BaseModel):
    deployment_id: str
    state: LifecycleState = LifecycleState.COLD
    last_transition: datetime = Field(default_factory=utcnow)
    idle_duration_seconds: int = 0


class ModelRegistrationRequest(BaseModel):
    name: str
    version: str
    family: str
    engine: str
    capabilities: list[Capability | str]
    memory_requirement_gb: int
    ownership: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeploymentCreateRequest(BaseModel):
    model_id: str
    endpoint: str
    engine: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
