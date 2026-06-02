"""Registry service implementation."""

from __future__ import annotations

from llm_platform.interfaces.registry import IRegistry
from llm_platform.interfaces.repositories import IDeploymentRepository, ILifecycleRepository, IModelRepository
from llm_platform.schemas.registry import (
    DeploymentCreateRequest,
    DeploymentRecord,
    LifecycleRecord,
    ModelRecord,
    ModelRegistrationRequest,
)


class RegistryService(IRegistry):
    """Service boundary for registry operations."""

    def __init__(
        self,
        model_repository: IModelRepository,
        deployment_repository: IDeploymentRepository,
        lifecycle_repository: ILifecycleRepository,
    ) -> None:
        self._model_repository = model_repository
        self._deployment_repository = deployment_repository
        self._lifecycle_repository = lifecycle_repository

    def register_model(self, request: ModelRegistrationRequest) -> ModelRecord:
        model = ModelRecord(**request.model_dump())
        return self._model_repository.save(model)

    def get_model(self, model_id: str) -> ModelRecord:
        return self._model_repository.get(model_id)

    def list_models(self) -> list[ModelRecord]:
        return self._model_repository.list()

    def update_model(self, model: ModelRecord) -> ModelRecord:
        return self._model_repository.save(model)

    def create_deployment(self, request: DeploymentCreateRequest) -> DeploymentRecord:
        deployment = DeploymentRecord(
            model_id=request.model_id,
            endpoint=request.endpoint,
            engine=request.engine or "",
            metadata=request.metadata,
        )
        return self._deployment_repository.save(deployment)

    def get_deployment(self, deployment_id: str) -> DeploymentRecord:
        return self._deployment_repository.get(deployment_id)

    def list_deployments(self) -> list[DeploymentRecord]:
        return self._deployment_repository.list()

    def update_deployment(self, deployment: DeploymentRecord) -> DeploymentRecord:
        return self._deployment_repository.save(deployment)

    def get_lifecycle(self, deployment_id: str) -> LifecycleRecord | None:
        return self._lifecycle_repository.get(deployment_id)

    def upsert_lifecycle(self, record: LifecycleRecord) -> LifecycleRecord:
        return self._lifecycle_repository.save(record)
