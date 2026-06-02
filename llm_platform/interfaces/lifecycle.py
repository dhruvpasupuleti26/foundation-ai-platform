"""Lifecycle interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord


class ILifecycleManager(ABC):
    """Abstract lifecycle manager contract."""

    @abstractmethod
    def initialize(self, deployment: DeploymentRecord) -> LifecycleRecord:
        """Create an initial lifecycle record for a deployment."""

    @abstractmethod
    def touch(self, record: LifecycleRecord) -> LifecycleRecord:
        """Mark a deployment as recently used."""

    @abstractmethod
    def reconcile(self, record: LifecycleRecord) -> LifecycleRecord:
        """Apply lifecycle policy transitions."""
