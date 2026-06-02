"""Gateway API schemas."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from llm_platform.schemas.enums import Capability
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord, ModelRegistrationRequest
from llm_platform.schemas.routing import RouteDecision


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    capability: Capability | str = Capability.CHAT
    messages: list[ChatMessage]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatCompletionResponse(BaseModel):
    request_id: str
    status: str
    route: RouteDecision
    message: str


class ModelRegisterRequest(ModelRegistrationRequest):
    pass


class ModelDeployRequest(DeploymentCreateRequest):
    pass


class ModelUnloadRequest(BaseModel):
    deployment_id: str


class ModelResponse(BaseModel):
    model: ModelRecord


class ModelsResponse(BaseModel):
    models: list[ModelRecord]


class DeploymentResponse(BaseModel):
    deployment: DeploymentRecord
