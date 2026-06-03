"""Compatibility checker implementation."""

from __future__ import annotations

from pathlib import Path

from llm_platform.compatibility.inspector import HuggingFaceModelInspector
from llm_platform.interfaces.compatibility import ICompatibilityChecker
from llm_platform.schemas.registry import DeploymentCreateRequest, ModelRecord
from llm_platform.schemas.validation import ValidationReport
from llm_platform.utils.errors import ValidationError


class DefaultCompatibilityChecker(ICompatibilityChecker):
    """Policy-based compatibility checks for the current platform scope."""

    def __init__(self, supported_engines: set[str], compatibility_config_path: str | Path | None = None) -> None:
        self._supported_engines = supported_engines
        config_path = compatibility_config_path or "configs/validation/backend_compatibility.yaml"
        self._inspector = HuggingFaceModelInspector(config_path)

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

    def inspect_huggingface_repo(self, hf_repo: str, revision: str | None = None) -> ValidationReport:
        """Inspect a Hugging Face repo and return a compatibility report."""
        return self._inspector.inspect(hf_repo, revision=revision)
