"""Compatibility interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from llm_platform.schemas.registry import DeploymentCreateRequest, ModelRecord


class ICompatibilityChecker(ABC):
    """Abstract compatibility contract."""

    @abstractmethod
    def validate_model(self, model: ModelRecord) -> None:
        """Validate model metadata."""

    @abstractmethod
    def validate_deployment(self, model: ModelRecord, request: DeploymentCreateRequest) -> None:
        """Validate a deployment request."""
