"""Compatibility checker implementation."""

from __future__ import annotations

from llm_platform.interfaces.compatibility import ICompatibilityChecker
from llm_platform.schemas.registry import DeploymentCreateRequest, ModelRecord
from llm_platform.utils.errors import ValidationError


class DefaultCompatibilityChecker(ICompatibilityChecker):
    """Policy-based compatibility checks for the current platform scope."""

    def __init__(self, supported_engines: set[str]) -> None:
        self._supported_engines = supported_engines

    def validate_model(self, model: ModelRecord) -> None:
        if not model.capabilities:
            raise ValidationError("Model must declare at least one capability.")
        if model.engine not in self._supported_engines:
            raise ValidationError(f"Unsupported engine: {model.engine}")

    def validate_deployment(self, model: ModelRecord, request: DeploymentCreateRequest) -> None:
        target_engine = request.engine or model.engine
        if target_engine != model.engine:
            raise ValidationError("Deployment engine must match model engine in the current platform phase.")
        if target_engine not in self._supported_engines:
            raise ValidationError(f"Unsupported deployment engine: {target_engine}")
