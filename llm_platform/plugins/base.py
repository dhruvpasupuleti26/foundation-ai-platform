"""Plugin base classes."""

from __future__ import annotations

from llm_platform.interfaces.plugin import IPlugin, PluginManifest


class BasePlugin(IPlugin):
    """Base plugin implementation with static manifest registration."""

    def __init__(self, manifest: PluginManifest) -> None:
        self._manifest = manifest

    @property
    def manifest(self) -> PluginManifest:
        return self._manifest

    def register(self) -> PluginManifest:
        return self._manifest
