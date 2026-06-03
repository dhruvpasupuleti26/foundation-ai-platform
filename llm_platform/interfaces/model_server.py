"""Serving engine abstractions.

This module defines the narrow contract that any runtime serving backend must
implement in order to participate in the platform. The rest of the platform
must depend on this interface instead of concrete backends such as vLLM or
Transformers so that engines can be swapped through configuration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.gateway import ChatCompletionRequest
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord


class IModelServer(ABC):
    """Abstract serving engine contract.

    Implementations own the engine-specific details required to load, unload,
    and execute inference for a deployment record. The platform core only sees
    `ModelRecord`, `DeploymentRecord`, and request schemas.
    """

    @abstractmethod
    def deploy(self, model: ModelRecord, request: DeploymentCreateRequest) -> DeploymentRecord:
        """Deploy a model and return deployment metadata.

        Args:
            model: Registered model metadata selected by the registry layer.
            request: Deployment request containing endpoint and runtime hints.

        Returns:
            A normalized deployment record that can be stored in the registry.
        """

    @abstractmethod
    def unload(self, deployment_id: str) -> None:
        """Unload a deployment.

        Args:
            deployment_id: Platform deployment identifier to remove from the
                serving backend.
        """

    @abstractmethod
    def health(self) -> dict[str, str | list[str]]:
        """Return serving backend health metadata.

        Returns:
            A small backend-specific health payload suitable for `GET /health`.
        """

    @abstractmethod
    def generate(self, deployment: DeploymentRecord, request: ChatCompletionRequest) -> str:
        """Generate model output for a deployment.

        Args:
            deployment: The selected deployment chosen by the router.
            request: Chat completion request provided by the gateway.

        Returns:
            Generated text content for the request.
        """
