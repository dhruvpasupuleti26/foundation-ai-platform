"""TGI Messages API client backend."""

from __future__ import annotations

from llm_platform.schemas.config import OpenAICompatibleBackendConfig
from llm_platform.serving.openai_compatible_remote import OpenAICompatibleRemoteModelServer


class TGIModelServer(OpenAICompatibleRemoteModelServer):
    """Remote client for TGI's OpenAI-compatible Messages API."""

    backend_name = "tgi-messages-api"

    def __init__(self, config: OpenAICompatibleBackendConfig) -> None:
        super().__init__(config)
