"""Mistral plugin manifest."""

from __future__ import annotations

from llm_platform.interfaces.plugin import PluginManifest
from llm_platform.plugins.base import BasePlugin


class MistralPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__(
            PluginManifest(
                plugin_id="mistral",
                family="mistral",
                supported_engines=["vllm", "huggingface-transformers"],
                capabilities=["chat", "embedding", "classification"],
            )
        )
