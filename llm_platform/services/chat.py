"""Chat request orchestration.

This module contains the application service responsible for request routing,
lightweight lifecycle updates, model-server invocation, and telemetry emission.
The service intentionally avoids transport and persistence details so it can be
tested in isolation.
"""

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
from llm_platform.utils.errors import NotFoundError


class ChatService:
    """Coordinate routing, lifecycle updates, and completion responses.

    The chat service is the main orchestration entrypoint for chat completions
    in the current platform phase. It locates eligible deployments through the
    router, delegates generation to the selected serving backend, and records
    telemetry for observability.
    """

    def __init__(
        self,
        registry: IRegistry,
        router: IRouter,
        lifecycle_manager: ILifecycleManager,
        telemetry_provider: ITelemetryProvider,
        model_server: IModelServer,
    ) -> None:
        """Initialize the chat orchestration service.

        Args:
            registry: Registry service used for models, deployments, and
                lifecycle state lookups.
            router: Capability-based router implementation.
            lifecycle_manager: Lifecycle manager used to touch deployments on
                successful use.
            telemetry_provider: Sink for request metrics and events.
            model_server: Serving backend responsible for actual generation.
        """
        self._registry = registry
        self._router = router
        self._lifecycle_manager = lifecycle_manager
        self._telemetry_provider = telemetry_provider
        self._model_server = model_server

    def create_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Create a chat completion response.

        Args:
            request: Gateway-level completion request.

        Returns:
            A platform response containing routing metadata and generated text.
        """
        started = perf_counter()
        models = self._registry.list_models()
        deployments = self._registry.list_deployments()
        preferred_model_id = self._resolve_requested_model_id(request, models)
        lifecycle_records = [record for record in (self._registry.get_lifecycle(d.deployment_id) for d in deployments) if record]
        route = self._router.route(
            RouteRequest(
                capability=request.capability,
                preferred_model_id=preferred_model_id,
                metadata=request.metadata,
            ),
            models=models,
            deployments=deployments,
            lifecycle_records=lifecycle_records,
        )
        deployment = self._registry.get_deployment(route.deployment_id)
        model = self._registry.get_model(route.model_id)
        lifecycle = self._registry.get_lifecycle(route.deployment_id)
        if lifecycle:
            self._registry.upsert_lifecycle(self._lifecycle_manager.touch(lifecycle))
        message = self._model_server.generate(deployment, request)
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

    def _resolve_requested_model_id(self, request: ChatCompletionRequest, models) -> str | None:
        """Resolve an explicitly requested model identifier or name.

        Args:
            request: Incoming chat completion request.
            models: Registered models available for routing.

        Returns:
            The selected preferred model id, if any.

        Raises:
            NotFoundError: If the request pins a model that does not exist.
        """
        if not request.model:
            return None
        for model in models:
            if model.id == request.model or model.name == request.model:
                return model.id
        raise NotFoundError(f"Requested model was not found in registry: {request.model}")
