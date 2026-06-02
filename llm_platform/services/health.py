"""Health reporting service."""

from __future__ import annotations

from llm_platform.interfaces.model_server import IModelServer
from llm_platform.interfaces.telemetry import ITelemetryProvider


class HealthService:
    """Expose lightweight health and metrics summaries."""

    def __init__(self, model_server: IModelServer, telemetry_provider: ITelemetryProvider) -> None:
        self._model_server = model_server
        self._telemetry_provider = telemetry_provider

    def health(self) -> dict[str, object]:
        return {
            "status": "ok",
            "serving": self._model_server.health(),
            "metrics": self._telemetry_provider.snapshot().model_dump(),
        }
