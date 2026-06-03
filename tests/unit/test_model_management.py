from __future__ import annotations

from llm_platform.compatibility.checker import DefaultCompatibilityChecker
from llm_platform.database.repositories import (
    InMemoryDeploymentRepository,
    InMemoryLifecycleRepository,
    InMemoryModelRepository,
)
from llm_platform.lifecycle.manager import SimpleLifecycleManager
from llm_platform.registry.service import RegistryService
from llm_platform.schemas.enums import Capability, DeploymentStatus, LifecycleState, ModelStatus
from llm_platform.schemas.registry import DeploymentCreateRequest, ModelRegistrationRequest
from llm_platform.services.model_management import ModelManagementService
from llm_platform.serving.fake_model_server import FakeModelServer


def test_deploy_model_updates_registry_and_lifecycle():
    registry = RegistryService(
        model_repository=InMemoryModelRepository(),
        deployment_repository=InMemoryDeploymentRepository(),
        lifecycle_repository=InMemoryLifecycleRepository(),
    )
    service = ModelManagementService(
        registry=registry,
        model_server=FakeModelServer(),
        compatibility_checker=DefaultCompatibilityChecker({"vllm", "huggingface-transformers"}),
        lifecycle_manager=SimpleLifecycleManager(),
    )
    model = service.register_model(
        ModelRegistrationRequest(
            name="chat-model",
            version="1.0.0",
            family="qwen",
            engine="vllm",
            capabilities=[Capability.CHAT],
            memory_requirement_gb=24,
            ownership="platform",
        )
    )

    deployment = service.deploy_model(
        DeploymentCreateRequest(model_id=model.id, endpoint="http://localhost:8001", engine="vllm")
    )

    lifecycle = registry.get_lifecycle(deployment.deployment_id)
    updated_model = registry.get_model(model.id)
    assert deployment.status == DeploymentStatus.READY
    assert lifecycle is not None and lifecycle.state == LifecycleState.HOT
    assert updated_model.status == ModelStatus.DEPLOYED
