from __future__ import annotations

from llm_platform.routing.router import CapabilityRouter
from llm_platform.schemas.enums import Capability, DeploymentStatus, LifecycleState, ModelStatus
from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.routing import RouteRequest


def test_router_selects_ready_deployment_for_capability():
    router = CapabilityRouter()
    model = ModelRecord(
        id="model-1",
        name="chat-model",
        version="1.0.0",
        family="qwen",
        engine="vllm",
        capabilities=[Capability.CHAT],
        memory_requirement_gb=24,
        ownership="platform",
        status=ModelStatus.DEPLOYED,
    )
    deployment = DeploymentRecord(
        deployment_id="dep-1",
        model_id="model-1",
        endpoint="http://localhost:8001",
        engine="vllm",
        status=DeploymentStatus.READY,
    )
    lifecycle = LifecycleRecord(deployment_id="dep-1", state=LifecycleState.HOT)

    decision = router.route(
        RouteRequest(capability=Capability.CHAT),
        models=[model],
        deployments=[deployment],
        lifecycle_records=[lifecycle],
    )

    assert decision.deployment_id == "dep-1"
    assert decision.model_id == "model-1"
