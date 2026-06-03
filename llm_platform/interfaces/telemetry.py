"""Telemetry interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.telemetry import MetricsSnapshot, TelemetryEvent


class ITelemetryProvider(ABC):
    """Abstract telemetry sink."""

    @abstractmethod
    def emit(self, event: TelemetryEvent) -> None:
        """Emit a telemetry event."""

    @abstractmethod
    def snapshot(self) -> MetricsSnapshot:
        """Return current aggregate metrics."""
