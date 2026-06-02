"""Chat request orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from llm_platform.interfaces.lifecycle import ILifecycleManager
from llm_platform.interfaces.model_server import IModelServer
from llm_platform.interfaces.registry import IRegistry
from llm_platform.interfaces.router import IRouter
from llm_platform.interfaces.telemetry import ITelemetryProvider
from llm_platform.schemas.gateway import ChatCompletionRequest, ChatCompletionResponse
from llm_platform.schemas.routing import RouteRequest
from llm_platform.schemas.telemetry import TelemetryEvent


class ChatService:
    """Coordinate routing, lifecycle updates, and placeholder completion responses."""

    def __init__(
        self,
        registry: IRegistry,
        router: IRouter,
        lifecycle_manager: ILifecycleManager,
        telemetry_provider: ITelemetryProvider,
        model_server: IModelServer,
    ) -> None:
        self._registry = registry
        self._router = router
        self._lifecycle_manager = lifecycle_manager
        self._telemetry_provider = telemetry_provider
        self._model_server = model_server

    def create_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        started = perf_counter()
        models = self._registry.list_models()
        deployments = self._registry.list_deployments()
        lifecycle_records = [record for record in (self._registry.get_lifecycle(d.deployment_id) for d in deployments) if record]
        route = self._router.route(
            RouteRequest(capability=request.capability, metadata=request.metadata),
            models=models,
            deployments=deployments,
            lifecycle_records=lifecycle_records,
        )
        deployment = self._registry.get_deployment(route.deployment_id)
        model = self._registry.get_model(route.model_id)
        lifecycle = self._registry.get_lifecycle(route.deployment_id)
        if lifecycle:
            self._registry.upsert_lifecycle(self._lifecycle_manager.touch(lifecycle))
        message = self._model_server.generate_placeholder(deployment, request)
        latency_ms = (perf_counter() - started) * 1000.0
        self._telemetry_provider.emit(
            TelemetryEvent(
                request_id=request.request_id,
                deployment_id=route.deployment_id,
                model_name=model.name,
                latency_ms=latency_ms,
                timestamp=datetime.now(timezone.utc),
                metadata={"capability": str(request.capability)},
            )
        )
        return ChatCompletionResponse(
            request_id=request.request_id,
            status="accepted",
            route=route,
            message=message,
        )
