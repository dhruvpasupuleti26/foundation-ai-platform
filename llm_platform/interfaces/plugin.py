"""Plugin interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    plugin_id: str
    family: str
    supported_engines: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class IPlugin(ABC):
    """Abstract plugin contract."""

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return plugin manifest."""

    @abstractmethod
    def register(self) -> PluginManifest:
        """Register plugin metadata with the platform."""
