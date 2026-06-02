"""Capability-based routing implementation."""

from __future__ import annotations

from llm_platform.interfaces.router import IRouter
from llm_platform.schemas.enums import DeploymentStatus, LifecycleState, ModelStatus
from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.routing import RouteDecision, RouteRequest
from llm_platform.utils.errors import RoutingError


class CapabilityRouter(IRouter):
    """Select the first healthy deployment that satisfies the requested capability."""

    def route(
        self,
        request: RouteRequest,
        models: list[ModelRecord],
        deployments: list[DeploymentRecord],
        lifecycle_records: list[LifecycleRecord],
    ) -> RouteDecision:
        lifecycle_by_deployment = {record.deployment_id: record for record in lifecycle_records}
        deployments_by_model = {deployment.model_id: deployment for deployment in deployments}

        for model in models:
            if model.status not in {ModelStatus.REGISTERED, ModelStatus.DEPLOYED}:
                continue
            if request.capability not in model.capabilities:
                continue
            deployment = deployments_by_model.get(model.id)
            if not deployment or deployment.status != DeploymentStatus.READY:
                continue
            lifecycle = lifecycle_by_deployment.get(deployment.deployment_id)
            if lifecycle and lifecycle.state == LifecycleState.FAILED:
                continue
            return RouteDecision(
                model_id=model.id,
                deployment_id=deployment.deployment_id,
                endpoint=deployment.endpoint,
                capability=request.capability,
                reason="matched capability with ready deployment",
            )

        raise RoutingError(f"No eligible deployment found for capability: {request.capability}")
