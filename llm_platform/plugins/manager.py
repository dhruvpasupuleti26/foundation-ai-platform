"""Plugin manager."""

from __future__ import annotations

from llm_platform.interfaces.plugin import IPlugin, PluginManifest
from llm_platform.utils.errors import ConflictError, NotFoundError


class PluginManager:
    """Register and expose plugin manifests."""

    def __init__(self) -> None:
        self._plugins: dict[str, IPlugin] = {}

    def register(self, plugin: IPlugin) -> PluginManifest:
        manifest = plugin.register()
        if manifest.plugin_id in self._plugins:
            raise ConflictError(f"Duplicate plugin id: {manifest.plugin_id}")
        self._plugins[manifest.plugin_id] = plugin
        return manifest

    def get(self, plugin_id: str) -> IPlugin:
        try:
            return self._plugins[plugin_id]
        except KeyError as error:
            raise NotFoundError(f"Plugin not found: {plugin_id}") from error

    def manifests(self) -> list[PluginManifest]:
        return [plugin.manifest for plugin in self._plugins.values()]
