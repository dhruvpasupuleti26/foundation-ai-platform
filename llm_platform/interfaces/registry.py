"""Registry interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.interfaces.repositories import IDeploymentRepository, ILifecycleRepository, IModelRepository
from llm_platform.schemas.registry import (
    DeploymentCreateRequest,
    DeploymentRecord,
    LifecycleRecord,
    ModelRecord,
    ModelRegistrationRequest,
)


class IRegistry(ABC):
    """Service-level registry contract."""

    @abstractmethod
    def register_model(self, request: ModelRegistrationRequest) -> ModelRecord:
        """Register a model in the registry."""

    @abstractmethod
    def get_model(self, model_id: str) -> ModelRecord:
        """Load a model by id."""

    @abstractmethod
    def list_models(self) -> list[ModelRecord]:
        """List all models."""

    @abstractmethod
    def update_model(self, model: ModelRecord) -> ModelRecord:
        """Persist a model update."""

    @abstractmethod
    def create_deployment(self, request: DeploymentCreateRequest) -> DeploymentRecord:
        """Create a deployment record."""

    @abstractmethod
    def get_deployment(self, deployment_id: str) -> DeploymentRecord:
        """Load deployment by id."""

    @abstractmethod
    def list_deployments(self) -> list[DeploymentRecord]:
        """List deployments."""

    @abstractmethod
    def update_deployment(self, deployment: DeploymentRecord) -> DeploymentRecord:
        """Persist a deployment update."""

    @abstractmethod
    def get_lifecycle(self, deployment_id: str) -> LifecycleRecord | None:
        """Load lifecycle record for a deployment."""

    @abstractmethod
    def upsert_lifecycle(self, record: LifecycleRecord) -> LifecycleRecord:
        """Create or update lifecycle state."""


__all__ = ["IRegistry", "IModelRepository", "IDeploymentRepository", "ILifecycleRepository"]
