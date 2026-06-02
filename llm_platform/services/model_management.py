"""Model registry and deployment orchestration."""

from __future__ import annotations

from llm_platform.interfaces.compatibility import ICompatibilityChecker
from llm_platform.interfaces.lifecycle import ILifecycleManager
from llm_platform.interfaces.model_server import IModelServer
from llm_platform.interfaces.registry import IRegistry
from llm_platform.schemas.enums import DeploymentStatus, ModelStatus
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord, ModelRegistrationRequest


class ModelManagementService:
    """Coordinate registry, compatibility, serving, and lifecycle concerns."""

    def __init__(
        self,
        registry: IRegistry,
        model_server: IModelServer,
        compatibility_checker: ICompatibilityChecker,
        lifecycle_manager: ILifecycleManager,
    ) -> None:
        self._registry = registry
        self._model_server = model_server
        self._compatibility_checker = compatibility_checker
        self._lifecycle_manager = lifecycle_manager

    def register_model(self, request: ModelRegistrationRequest) -> ModelRecord:
        model = ModelRecord(**request.model_dump())
        self._compatibility_checker.validate_model(model)
        return self._registry.register_model(request)

    def deploy_model(self, request: DeploymentCreateRequest) -> DeploymentRecord:
        model = self._registry.get_model(request.model_id)
        self._compatibility_checker.validate_deployment(model, request)
        deployment = self._model_server.deploy(model, request)
        deployment = deployment.model_copy(update={"status": DeploymentStatus.READY})
        self._registry.update_deployment(deployment)
        self._registry.upsert_lifecycle(self._lifecycle_manager.initialize(deployment))
        updated_model = model.model_copy(update={"status": ModelStatus.DEPLOYED})
        self._registry.update_model(updated_model)
        return deployment

    def unload_model(self, deployment_id: str) -> DeploymentRecord:
        deployment = self._registry.get_deployment(deployment_id)
        self._model_server.unload(deployment_id)
        deployment = deployment.model_copy(update={"status": DeploymentStatus.UNLOADED})
        return self._registry.update_deployment(deployment)

    def list_models(self) -> list[ModelRecord]:
        return self._registry.list_models()

    def get_model(self, model_id: str) -> ModelRecord:
        return self._registry.get_model(model_id)
