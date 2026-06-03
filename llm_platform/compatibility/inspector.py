"""Hugging Face model inspection and backend recommendation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from llm_platform.schemas.validation import ValidationReport
from llm_platform.utils.errors import ValidationError


class HuggingFaceModelInspector:
    """Inspect Hugging Face model metadata and recommend a serving backend."""

    def __init__(self, compatibility_config_path: str | Path) -> None:
        """Initialize the inspector.

        Args:
            compatibility_config_path: YAML file describing architecture to
                backend compatibility rules.
        """
        self._config = self._load_config(compatibility_config_path)

    def inspect(self, hf_repo: str, revision: str | None = None) -> ValidationReport:
        """Inspect a Hugging Face repository and produce a compatibility report.

        Args:
            hf_repo: Hugging Face model repository id.
            revision: Optional revision or branch.

        Returns:
            Structured validation report.
        """
        try:
            from huggingface_hub import HfApi
            from transformers import AutoConfig, AutoTokenizer
        except ImportError as error:
            raise ValidationError(
                "Validation tooling requires `huggingface_hub` and `transformers`. Install inference dependencies first."
            ) from error

        api = HfApi()
        info = api.model_info(hf_repo, revision=revision)
        config = AutoConfig.from_pretrained(hf_repo, revision=revision)
        tokenizer = AutoTokenizer.from_pretrained(hf_repo, revision=revision, trust_remote_code=False)
        architecture = (getattr(config, "architectures", None) or [None])[0]
        estimated_gpu_memory_gb = None
        if info.safetensors and getattr(info.safetensors, "total", None):
            estimated_gpu_memory_gb = round(float(info.safetensors.total) / (1024**3), 2)
        recommended_backend, compatibility = self._choose_backend(architecture)
        notes: list[str] = []
        if not getattr(tokenizer, "chat_template", None):
            notes.append("Tokenizer does not expose a chat template. Gateway chat proxy may require a configured template.")
        if estimated_gpu_memory_gb is not None:
            notes.append(
                "Estimated GPU memory is derived from safetensors weight size and should be treated as a lower bound, not full runtime residency."
            )

        return ValidationReport(
            hf_repo=hf_repo,
            revision=revision,
            architecture=architecture,
            tokenizer_status="ok",
            chat_template_status="ok" if getattr(tokenizer, "chat_template", None) else "missing",
            config_status="ok",
            compatibility=compatibility,
            recommended_backend=recommended_backend,
            estimated_gpu_memory_gb=estimated_gpu_memory_gb,
            max_context_length=getattr(config, "max_position_embeddings", None),
            notes=notes,
            metadata={
                "model_sha": info.sha,
                "private": info.private,
                "library_name": info.library_name,
            },
        )

    def _choose_backend(self, architecture: str | None) -> tuple[str, str]:
        """Choose a backend using config-driven architecture rules."""
        rules = self._config.get("architectures", {})
        vllm_native = set(rules.get("vllm_native", []))
        tgi_supported = set(rules.get("tgi", []))
        transformers_supported = set(rules.get("transformers_fallback", []))
        if architecture in vllm_native:
            return "vllm", "vllm_native"
        if architecture in tgi_supported:
            return "tgi", "tgi_messages_api"
        if architecture in transformers_supported or architecture is not None:
            return "huggingface-transformers", "transformers_fallback"
        return "manual_review", "unsupported"

    def _load_config(self, path: str | Path) -> dict[str, Any]:
        """Load backend compatibility rules from YAML."""
        candidate = Path(path)
        with candidate.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
