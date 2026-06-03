"""HuggingFace Transformers serving backend.

This module provides a lightweight in-process runtime suitable for local
development, smoke tests, and CPU or MPS-backed experimentation. It is not a
replacement for production multi-tenant serving engines such as vLLM, but it
allows the platform scaffold to execute real model inference through the same
service interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any

from llm_platform.interfaces.model_server import IModelServer
from llm_platform.schemas.config import ServingConfig
from llm_platform.schemas.gateway import ChatCompletionRequest
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord
from llm_platform.serving.placement import discover_placement_availability, resolve_placement
from llm_platform.utils.errors import NotFoundError, ValidationError


@dataclass(slots=True)
class _LoadedDeployment:
    """Internal runtime container for a loaded deployment."""

    model_name: str
    source_model_id: str
    placement: str
    tokenizer: Any
    model: Any


class HuggingFaceModelServer(IModelServer):
    """In-process Transformers backend with placement-aware loading.

    The server maintains a deployment-id keyed in-memory registry of loaded
    tokenizers and models. This is sufficient for local smoke tests and early
    integration work where a single process owns the deployment lifecycle.
    """

    def __init__(self, config: ServingConfig) -> None:
        """Initialize the Transformers model server.

        Args:
            config: Serving runtime configuration.
        """
        self._config = config
        self._loaded_deployments: dict[str, _LoadedDeployment] = {}
        self._lock = RLock()

    def deploy(self, model: ModelRecord, request: DeploymentCreateRequest) -> DeploymentRecord:
        """Load a model into the local process.

        Args:
            model: Registered model metadata.
            request: Deployment request containing placement and source hints.

        Returns:
            A deployment record annotated with resolved runtime metadata.
        """
        runtime = self._lazy_runtime_imports()
        source_model_id = self._resolve_source_model_id(model, request)
        placement = resolve_placement(
            preferred=request.placement or self._config.default_placement,
            fallbacks=request.fallback_placements or self._config.fallback_placements,
            availability=discover_placement_availability(),
        )
        cache_dir = Path(self._config.model_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        torch_dtype = self._resolve_torch_dtype(runtime.torch, placement)
        tokenizer = runtime.AutoTokenizer.from_pretrained(
            source_model_id,
            revision=self._config.huggingface.revision,
            trust_remote_code=self._config.huggingface.trust_remote_code,
            cache_dir=str(cache_dir),
        )
        loaded_model = runtime.AutoModelForCausalLM.from_pretrained(
            source_model_id,
            revision=self._config.huggingface.revision,
            trust_remote_code=self._config.huggingface.trust_remote_code,
            cache_dir=str(cache_dir),
            dtype=torch_dtype,
        )
        loaded_model.to(placement)
        loaded_model.eval()

        deployment = DeploymentRecord(
            model_id=model.id,
            endpoint=request.endpoint,
            engine=request.engine or model.engine,
            status="ready",
            metadata={
                **request.metadata,
                "source_model_id": source_model_id,
                "placement": placement,
                "implementation": "huggingface-transformers",
            },
        )

        with self._lock:
            self._loaded_deployments[deployment.deployment_id] = _LoadedDeployment(
                model_name=model.name,
                source_model_id=source_model_id,
                placement=placement,
                tokenizer=tokenizer,
                model=loaded_model,
            )
        return deployment

    def unload(self, deployment_id: str) -> None:
        """Unload a deployment from memory.

        Args:
            deployment_id: Platform deployment identifier.
        """
        with self._lock:
            loaded = self._loaded_deployments.pop(deployment_id, None)
        if loaded is None:
            raise NotFoundError(f"Deployment not loaded: {deployment_id}")
        try:
            import gc
            import torch

            del loaded
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            mps_backend = getattr(getattr(torch, "mps", None), "empty_cache", None)
            if callable(mps_backend):
                mps_backend()
        except ImportError:
            return

    def health(self) -> dict[str, str | list[str]]:
        """Return backend health and placement support metadata."""
        availability = discover_placement_availability()
        return {
            "status": "ok",
            "backend": "huggingface-transformers",
            "placements": availability.as_list(),
        }

    def generate(self, deployment: DeploymentRecord, request: ChatCompletionRequest) -> str:
        """Generate a response for a chat completion request.

        Args:
            deployment: Selected deployment.
            request: Chat completion request.

        Returns:
            Generated assistant text.
        """
        runtime = self._lazy_runtime_imports()
        with self._lock:
            loaded = self._loaded_deployments.get(deployment.deployment_id)
        if loaded is None:
            raise NotFoundError(f"Deployment not loaded: {deployment.deployment_id}")

        messages = [message.model_dump() for message in request.messages]
        template_kwargs: dict[str, Any] = {}
        if "enable_thinking" in request.metadata:
            template_kwargs["enable_thinking"] = bool(request.metadata["enable_thinking"])
        inputs = loaded.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            **template_kwargs,
        )
        inputs = {name: tensor.to(loaded.placement) for name, tensor in inputs.items()}
        generation_defaults = self._config.huggingface.generation
        do_sample = bool(request.metadata.get("do_sample", generation_defaults.do_sample))
        generation_kwargs: dict[str, Any] = {
            "max_new_tokens": int(request.metadata.get("max_new_tokens", generation_defaults.max_new_tokens)),
            "do_sample": do_sample,
        }
        if do_sample:
            generation_kwargs["temperature"] = float(request.metadata.get("temperature", generation_defaults.temperature))
            generation_kwargs["top_p"] = float(request.metadata.get("top_p", generation_defaults.top_p))
        generated = loaded.model.generate(**inputs, **generation_kwargs)
        prompt_length = inputs["input_ids"].shape[-1]
        completion_ids = generated[0][prompt_length:]
        return loaded.tokenizer.decode(completion_ids, skip_special_tokens=True).strip()

    def _resolve_source_model_id(self, model: ModelRecord, request: DeploymentCreateRequest) -> str:
        """Resolve the upstream model identifier for `from_pretrained`.

        Args:
            model: Registered platform model.
            request: Deployment request.

        Returns:
            The source model identifier.

        Raises:
            ValidationError: If no upstream model identifier is provided.
        """
        source_model_id = (
            request.metadata.get("source_model_id")
            or model.metadata.get("source_model_id")
            or model.metadata.get("huggingface_model_id")
        )
        if not source_model_id:
            raise ValidationError(
                "HuggingFace deployments require `source_model_id` in model metadata or deployment metadata."
            )
        return str(source_model_id)

    def _resolve_torch_dtype(self, torch_module: Any, placement: str) -> Any:
        """Resolve a safe runtime dtype for the selected placement."""
        configured = self._config.huggingface.default_dtype.lower()
        if configured == "auto":
            if placement == "cpu":
                return torch_module.float32
            return torch_module.float16
        if not hasattr(torch_module, configured):
            raise ValidationError(f"Unsupported torch dtype configured for HuggingFace backend: {configured}")
        return getattr(torch_module, configured)

    def _lazy_runtime_imports(self):
        """Import runtime ML dependencies only when the backend is used."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as error:
            raise ValidationError(
                "HuggingFace runtime dependencies are missing. Install `.[inference]` before using this backend."
            ) from error

        @dataclass(slots=True)
        class _Runtime:
            torch: Any
            AutoTokenizer: Any
            AutoModelForCausalLM: Any

        return _Runtime(torch=torch, AutoTokenizer=AutoTokenizer, AutoModelForCausalLM=AutoModelForCausalLM)
