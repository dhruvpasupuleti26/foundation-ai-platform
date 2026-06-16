"""Capability-based routing implementation."""

from __future__ import annotations

import random

from llm_platform.interfaces.router import IRouter
from llm_platform.schemas.enums import DeploymentStatus, LifecycleState, ModelStatus
from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.routing import RouteDecision, RouteRequest
from llm_platform.utils.errors import RoutingError


class CapabilityRouter(IRouter):
    """Select a healthy deployment that satisfies the requested capability with load balancing."""

    def route(
        self,
        request: RouteRequest,
        models: list[ModelRecord],
        deployments: list[DeploymentRecord],
        lifecycle_records: list[LifecycleRecord],
    ) -> RouteDecision:
        lifecycle_by_deployment = {record.deployment_id: record for record in lifecycle_records}
        deployments_by_model = {deployment.model_id: deployment for deployment in deployments}
        
        ready_deployments = []
        unloaded_deployments = []

        for model in models:
            if model.status not in {ModelStatus.REGISTERED, ModelStatus.DEPLOYED}:
                continue
            if request.capability not in model.capabilities:
                continue
            deployment = deployments_by_model.get(model.id)
            if not deployment:
                continue
                
            lifecycle = lifecycle_by_deployment.get(deployment.deployment_id)
            if lifecycle and lifecycle.state == LifecycleState.FAILED:
                continue
                
            if deployment.status == DeploymentStatus.READY:
                if request.preferred_model_id and model.id == request.preferred_model_id:
                    return RouteDecision(
                        model_id=model.id,
                        deployment_id=deployment.deployment_id,
                        endpoint=deployment.endpoint,
                        capability=request.capability,
                        reason="matched preferred model and capability with ready deployment",
                        requires_cold_start=False
                    )
                ready_deployments.append((model, deployment))
            elif deployment.status == DeploymentStatus.UNLOADED:
                unloaded_deployments.append((model, deployment))

        if ready_deployments:
            selected_model, selected_deployment = random.choice(ready_deployments)
            return RouteDecision(
                model_id=selected_model.id,
                deployment_id=selected_deployment.deployment_id,
                endpoint=selected_deployment.endpoint,
                capability=request.capability,
                reason="Load balanced across ready deployments",
                requires_cold_start=False
            )

        if unloaded_deployments:
            selected_model, selected_deployment = random.choice(unloaded_deployments)
            return RouteDecision(
                model_id=selected_model.id,
                deployment_id=selected_deployment.deployment_id,
                endpoint=selected_deployment.endpoint,
                capability=request.capability,
                reason="Cold start required for unloaded deployment",
                requires_cold_start=True
            )

        raise RoutingError(f"No eligible deployment found for capability: {request.capability}")

