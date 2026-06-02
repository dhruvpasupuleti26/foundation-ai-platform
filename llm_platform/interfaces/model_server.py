"""Serving engine abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.gateway import ChatCompletionRequest
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord


class IModelServer(ABC):
    """Abstract serving engine contract."""

    @abstractmethod
    def deploy(self, model: ModelRecord, request: DeploymentCreateRequest) -> DeploymentRecord:
        """Deploy a model and return deployment metadata."""

    @abstractmethod
    def unload(self, deployment_id: str) -> None:
        """Unload a deployment."""

    @abstractmethod
    def health(self) -> dict[str, str]:
        """Return serving backend health metadata."""

    @abstractmethod
    def generate_placeholder(self, deployment: DeploymentRecord, request: ChatCompletionRequest) -> str:
        """Return a placeholder response until inference is implemented."""
