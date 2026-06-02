from __future__ import annotations

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.schemas.config import PlatformConfig, PluginConfig


def test_builder_registers_enabled_plugins():
    config = PlatformConfig(plugins=PluginConfig(enabled=["qwen", "mistral"]))

    application = PlatformApplicationBuilder().build_from_config(config)

    manifests = application.plugin_manager.manifests()
    assert {manifest.plugin_id for manifest in manifests} == {"qwen", "mistral"}
