"""Serving backend factory.

The builder uses this module to translate configuration into a concrete model
server implementation. Keeping the logic in one place prevents ad-hoc backend
selection from leaking across the codebase.
"""

from __future__ import annotations

from llm_platform.interfaces.model_server import IModelServer
from llm_platform.schemas.config import ServingConfig
from llm_platform.serving.fake_model_server import FakeModelServer
from llm_platform.serving.huggingface_model_server import HuggingFaceModelServer
from llm_platform.serving.tgi_client import TGIModelServer
from llm_platform.serving.vllm_client import VLLMModelServer
from llm_platform.utils.errors import ValidationError


def build_model_server(config: ServingConfig) -> IModelServer:
    """Build the configured model server implementation.

    Args:
        config: Serving runtime configuration.

    Returns:
        Configured model server implementation.

    Raises:
        ValidationError: If the implementation value is unknown.
    """
    implementation = config.implementation.lower()
    if implementation == "fake":
        return FakeModelServer()
    if implementation in {"huggingface-transformers", "transformers-local"}:
        return HuggingFaceModelServer(config)
    if implementation in {"vllm", "vllm-openai"}:
        return VLLMModelServer(config.vllm)
    if implementation in {"tgi", "tgi-messages-api"}:
        return TGIModelServer(config.tgi)
    raise ValidationError(f"Unsupported serving implementation: {config.implementation}")
