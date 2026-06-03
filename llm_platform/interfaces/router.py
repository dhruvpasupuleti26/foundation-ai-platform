"""Routing interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.routing import RouteDecision, RouteRequest


class IRouter(ABC):
    """Abstract routing contract."""

    @abstractmethod
    def route(
        self,
        request: RouteRequest,
        models: list[ModelRecord],
        deployments: list[DeploymentRecord],
        lifecycle_records: list[LifecycleRecord],
    ) -> RouteDecision:
        """Select a compatible deployment for the request."""
