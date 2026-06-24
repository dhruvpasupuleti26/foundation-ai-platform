"""Capability-based routing with GPU-aware scheduling.

Decision tree:
1. Find all models matching the requested capability.
2. Among their deployments:
   a. READY + idle (lifecycle HOT/WARM) → serve immediately, prefer models
      with the most capabilities (breadth-first), then random tie-break.
   b. All READY but occupied → check GPU for space:
      - Space available → requires_new_instance=True
      - No space → find idle model to evict → evict_deployment_id set
   c. UNLOADED → cold start (existing behavior)
3. No deployment at all → raise RoutingError
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from llm_platform.interfaces.router import IRouter
from llm_platform.schemas.enums import DeploymentStatus, LifecycleState, ModelStatus
from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.routing import RouteDecision, RouteRequest
from llm_platform.utils.errors import RoutingError

if TYPE_CHECKING:
    from llm_platform.services.gpu_tracker import GPUResourceTracker

logger = logging.getLogger(__name__)


class CapabilityRouter(IRouter):
    """Select a healthy deployment that satisfies the requested capability with
    GPU-aware scheduling, load balancing, and eviction support."""

    def __init__(self, gpu_tracker: "GPUResourceTracker | None" = None) -> None:
        self._gpu_tracker = gpu_tracker

    def route(
        self,
        request: RouteRequest,
        models: list[ModelRecord],
        deployments: list[DeploymentRecord],
        lifecycle_records: list[LifecycleRecord],
    ) -> RouteDecision:
        lifecycle_by_deployment = {r.deployment_id: r for r in lifecycle_records}

        # Build a map of model_id -> list[deployment] (multiple containers possible)
        deployments_by_model: dict[str, list[DeploymentRecord]] = {}
        for dep in deployments:
            deployments_by_model.setdefault(dep.model_id, []).append(dep)

        # ── Phase 1: Collect capable models ──────────────────────────
        capable_models: list[ModelRecord] = []
        for model in models:
            if model.status not in {ModelStatus.REGISTERED, ModelStatus.DEPLOYED}:
                continue
            if request.capability not in model.capabilities:
                continue
            capable_models.append(model)

        if not capable_models:
            raise RoutingError(
                f"No model registered with capability: {request.capability}"
            )

        # Sort capable models by capability breadth (more capabilities = more reusable)
        capable_models.sort(key=lambda m: len(m.capabilities), reverse=True)

        # ── Phase 2: Categorize deployments ──────────────────────────
        ready_idle: list[tuple[ModelRecord, DeploymentRecord]] = []
        ready_busy: list[tuple[ModelRecord, DeploymentRecord]] = []
        unloaded: list[tuple[ModelRecord, DeploymentRecord]] = []

        for model in capable_models:
            model_deployments = deployments_by_model.get(model.id, [])
            if not model_deployments:
                continue

            for dep in model_deployments:
                lifecycle = lifecycle_by_deployment.get(dep.deployment_id)
                if lifecycle and lifecycle.state == LifecycleState.FAILED:
                    continue

                if dep.status == DeploymentStatus.READY:
                    # Preferred model shortcut
                    if request.preferred_model_id and model.id == request.preferred_model_id:
                        return RouteDecision(
                            model_id=model.id,
                            deployment_id=dep.deployment_id,
                            endpoint=dep.endpoint,
                            capability=request.capability,
                            reason="Matched preferred model and capability with ready deployment",
                            requires_cold_start=False,
                        )

                    if lifecycle and lifecycle.state in {LifecycleState.HOT, LifecycleState.WARM}:
                        ready_idle.append((model, dep))
                    else:
                        # HOT lifecycle not yet initialized, treat as idle too
                        ready_idle.append((model, dep))
                elif dep.status == DeploymentStatus.UNLOADED:
                    unloaded.append((model, dep))

        # ── Phase 3: Route Decision ──────────────────────────────────

        # 3a. Serve from idle READY deployment (load balanced)
        if ready_idle:
            selected_model, selected_dep = random.choice(ready_idle)
            return RouteDecision(
                model_id=selected_model.id,
                deployment_id=selected_dep.deployment_id,
                endpoint=selected_dep.endpoint,
                capability=request.capability,
                reason=f"Load balanced across {len(ready_idle)} idle deployment(s) "
                       f"(model has {len(selected_model.capabilities)} capabilities)",
                requires_cold_start=False,
            )

        # 3b. All READY deployments are busy — try to spin up another container
        if ready_busy and self._gpu_tracker:
            # Pick the model with the most capabilities for maximum reuse
            best_model = capable_models[0]
            best_dep = (deployments_by_model.get(best_model.id, [None]) or [None])[0]
            if best_dep:
                if self._gpu_tracker.can_fit(best_model.memory_requirement_gb):
                    return RouteDecision(
                        model_id=best_model.id,
                        deployment_id=best_dep.deployment_id,
                        endpoint=best_dep.endpoint,
                        capability=request.capability,
                        reason=f"GPU has space ({self._gpu_tracker.available_vram_gb}GB free), "
                               f"spinning up new instance",
                        requires_cold_start=False,
                        requires_new_instance=True,
                    )
                else:
                    # GPU full — try to evict an idle model
                    evict_id = self._gpu_tracker.find_evictable(
                        # We'll need registry access — passed via metadata
                        request.metadata.get("_registry"),
                        best_model.memory_requirement_gb,
                    )
                    if evict_id:
                        return RouteDecision(
                            model_id=best_model.id,
                            deployment_id=best_dep.deployment_id,
                            endpoint=best_dep.endpoint,
                            capability=request.capability,
                            reason=f"GPU full, evicting idle deployment {evict_id} to make room",
                            requires_cold_start=False,
                            requires_new_instance=True,
                            evict_deployment_id=evict_id,
                        )

        # 3c. Cold start from unloaded deployment
        if unloaded:
            # Check GPU space for cold start
            selected_model, selected_dep = unloaded[0]  # Pick first (highest capability breadth)

            if self._gpu_tracker:
                if self._gpu_tracker.can_fit(selected_model.memory_requirement_gb):
                    return RouteDecision(
                        model_id=selected_model.id,
                        deployment_id=selected_dep.deployment_id,
                        endpoint=selected_dep.endpoint,
                        capability=request.capability,
                        reason=f"Cold start — GPU has {self._gpu_tracker.available_vram_gb}GB free",
                        requires_cold_start=True,
                    )
                else:
                    # Try eviction for cold start too
                    evict_id = self._gpu_tracker.find_evictable(
                        request.metadata.get("_registry"),
                        selected_model.memory_requirement_gb,
                    )
                    if evict_id:
                        return RouteDecision(
                            model_id=selected_model.id,
                            deployment_id=selected_dep.deployment_id,
                            endpoint=selected_dep.endpoint,
                            capability=request.capability,
                            reason=f"Cold start — evicting {evict_id} to free GPU space",
                            requires_cold_start=True,
                            evict_deployment_id=evict_id,
                        )
                    raise RoutingError(
                        f"GPU full ({self._gpu_tracker.allocated_vram_gb}/"
                        f"{self._gpu_tracker.total_vram_gb}GB) and no idle deployment to evict "
                        f"for capability: {request.capability}"
                    )
            else:
                # No GPU tracker — simple cold start
                return RouteDecision(
                    model_id=selected_model.id,
                    deployment_id=selected_dep.deployment_id,
                    endpoint=selected_dep.endpoint,
                    capability=request.capability,
                    reason="Cold start required for unloaded deployment",
                    requires_cold_start=True,
                )

        raise RoutingError(
            f"No eligible deployment found for capability: {request.capability}"
        )
