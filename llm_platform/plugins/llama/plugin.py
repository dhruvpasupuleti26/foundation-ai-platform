"""Llama plugin manifest."""

from __future__ import annotations

from llm_platform.interfaces.plugin import PluginManifest
from llm_platform.plugins.base import BasePlugin


class LlamaPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__(
            PluginManifest(
                plugin_id="llama",
                family="llama",
                supported_engines=["vllm", "huggingface-transformers"],
                capabilities=["chat", "reasoning"],
            )
        )
