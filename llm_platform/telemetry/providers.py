"""Telemetry provider implementations."""

from __future__ import annotations

from llm_platform.interfaces.repositories import ITelemetryRepository
from llm_platform.interfaces.telemetry import ITelemetryProvider
from llm_platform.schemas.telemetry import MetricsSnapshot, TelemetryEvent


class NoOpTelemetryProvider(ITelemetryProvider):
    """Null object telemetry provider."""

    def emit(self, event: TelemetryEvent) -> None:
        del event

    def snapshot(self) -> MetricsSnapshot:
        return MetricsSnapshot()


class MemoryTelemetryProvider(ITelemetryProvider):
    """In-memory telemetry sink used for tests and local development."""

    def __init__(self, repository: ITelemetryRepository) -> None:
        self._repository = repository

    def emit(self, event: TelemetryEvent) -> None:
        self._repository.save(event)

    def snapshot(self) -> MetricsSnapshot:
        return self._repository.snapshot()


class RepositoryTelemetryProvider(ITelemetryProvider):
    """Telemetry provider backed by a repository implementation."""

    def __init__(self, repository: ITelemetryRepository) -> None:
        self._repository = repository

    def emit(self, event: TelemetryEvent) -> None:
        self._repository.save(event)

    def snapshot(self) -> MetricsSnapshot:
        return self._repository.snapshot()
