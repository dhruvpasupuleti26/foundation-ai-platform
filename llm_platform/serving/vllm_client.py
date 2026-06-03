"""vLLM OpenAI-compatible client backend."""

from __future__ import annotations

from llm_platform.schemas.config import OpenAICompatibleBackendConfig
from llm_platform.serving.openai_compatible_remote import OpenAICompatibleRemoteModelServer


class VLLMModelServer(OpenAICompatibleRemoteModelServer):
    """Remote client for vLLM's OpenAI-compatible server."""

    backend_name = "vllm-openai"

    def __init__(self, config: OpenAICompatibleBackendConfig) -> None:
        super().__init__(config)
