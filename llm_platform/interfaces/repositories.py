"""Repository interfaces isolated from SQLAlchemy implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.telemetry import MetricsSnapshot, TelemetryEvent


class IModelRepository(ABC):
    """Persistence contract for model records."""

    @abstractmethod
    def save(self, model: ModelRecord) -> ModelRecord:
        """Create or update a model record."""

    @abstractmethod
    def get(self, model_id: str) -> ModelRecord:
        """Load a model by id."""

    @abstractmethod
    def list(self) -> list[ModelRecord]:
        """List models."""


class IDeploymentRepository(ABC):
    """Persistence contract for deployment records."""

    @abstractmethod
    def save(self, deployment: DeploymentRecord) -> DeploymentRecord:
        """Create or update a deployment record."""

    @abstractmethod
    def get(self, deployment_id: str) -> DeploymentRecord:
        """Load a deployment by id."""

    @abstractmethod
    def list(self) -> list[DeploymentRecord]:
        """List deployments."""


class ILifecycleRepository(ABC):
    """Persistence contract for lifecycle records."""

    @abstractmethod
    def save(self, record: LifecycleRecord) -> LifecycleRecord:
        """Create or update a lifecycle record."""

    @abstractmethod
    def get(self, deployment_id: str) -> LifecycleRecord | None:
        """Load lifecycle state for a deployment."""

    @abstractmethod
    def list(self) -> list[LifecycleRecord]:
        """List lifecycle records."""


class ITelemetryRepository(ABC):
    """Persistence contract for telemetry events."""

    @abstractmethod
    def save(self, event: TelemetryEvent) -> TelemetryEvent:
        """Persist a telemetry event."""

    @abstractmethod
    def list(self) -> list[TelemetryEvent]:
        """List telemetry events."""

    @abstractmethod
    def snapshot(self) -> MetricsSnapshot:
        """Return aggregate metrics."""
