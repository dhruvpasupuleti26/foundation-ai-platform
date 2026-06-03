"""Application bootstrap and dependency wiring.

This module assembles the platform from validated configuration and interface-
backed implementations. It is intentionally explicit rather than magical so the
wiring remains understandable as the repository grows.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from llm_platform.compatibility.checker import DefaultCompatibilityChecker
from llm_platform.database.repositories import (
    InMemoryDeploymentRepository,
    InMemoryLifecycleRepository,
    InMemoryModelRepository,
    InMemoryTelemetryRepository,
    SQLAlchemyDeploymentRepository,
    SQLAlchemyLifecycleRepository,
    SQLAlchemyModelRepository,
    SQLAlchemyTelemetryRepository,
)
from llm_platform.database.session import DatabaseSessionManager
from llm_platform.interfaces.compatibility import ICompatibilityChecker
from llm_platform.interfaces.lifecycle import ILifecycleManager
from llm_platform.interfaces.model_server import IModelServer
from llm_platform.interfaces.registry import IRegistry
from llm_platform.interfaces.router import IRouter
from llm_platform.interfaces.telemetry import ITelemetryProvider
from llm_platform.lifecycle.manager import SimpleLifecycleManager
from llm_platform.plugins.deepseek import DeepSeekPlugin
from llm_platform.plugins.llama import LlamaPlugin
from llm_platform.plugins.manager import PluginManager
from llm_platform.plugins.mistral import MistralPlugin
from llm_platform.plugins.qwen import QwenPlugin
from llm_platform.registry.service import RegistryService
from llm_platform.routing.router import CapabilityRouter
from llm_platform.schemas.config import PlatformConfig
from llm_platform.services.chat import ChatService
from llm_platform.services.health import HealthService
from llm_platform.services.model_management import ModelManagementService
from llm_platform.serving.factory import build_model_server
from llm_platform.telemetry.providers import MemoryTelemetryProvider, NoOpTelemetryProvider, RepositoryTelemetryProvider
from llm_platform.utils.config_loader import ConfigLoader

if TYPE_CHECKING:
    from fastapi import FastAPI


@dataclass(slots=True)
class PlatformApplication:
    """Assembled platform dependencies.

    Attributes:
        config: Validated platform configuration.
        registry: Registry service used across the application.
        router: Capability-based routing implementation.
        lifecycle_manager: Lifecycle manager for deployment state.
        telemetry_provider: Active telemetry sink.
        compatibility_checker: Validation layer for model compatibility.
        model_server: Active serving backend implementation.
        plugin_manager: Registered plugin manager instance.
        model_management_service: Service for registration and deployment
            workflows.
        chat_service: Service for completion workflows.
        health_service: Service for health and metrics summary.
    """

    config: PlatformConfig
    registry: IRegistry
    router: IRouter
    lifecycle_manager: ILifecycleManager
    telemetry_provider: ITelemetryProvider
    compatibility_checker: ICompatibilityChecker
    model_server: IModelServer
    plugin_manager: PluginManager
    model_management_service: ModelManagementService
    chat_service: ChatService
    health_service: HealthService


class PlatformApplicationBuilder:
    """Create a platform application from configuration."""

    def __init__(self, config_loader: ConfigLoader | None = None) -> None:
        """Initialize the application builder.

        Args:
            config_loader: Optional configuration loader override for tests or
                custom environments.
        """
        self._config_loader = config_loader or ConfigLoader()

    def build_from_file(self, path: str | Path = "configs/platform.yaml") -> PlatformApplication:
        """Build an application from a YAML configuration file.

        Args:
            path: Path to the platform configuration file.

        Returns:
            Fully assembled application container.
        """
        config = self._config_loader.load(path, PlatformConfig)
        return self.build_from_config(config)

    def build_from_config(self, config: PlatformConfig) -> PlatformApplication:
        """Build an application from an already validated config object."""
        plugin_manager = self._build_plugins(config)
        model_repository, deployment_repository, lifecycle_repository, telemetry_repository = self._build_repositories(
            config
        )
        registry = RegistryService(
            model_repository=model_repository,
            deployment_repository=deployment_repository,
            lifecycle_repository=lifecycle_repository,
        )
        lifecycle_manager = SimpleLifecycleManager()
        router = CapabilityRouter()
        model_server = build_model_server(config.serving)
        compatibility_checker = DefaultCompatibilityChecker(
            set(config.serving.supported_engines),
            compatibility_config_path="configs/validation/backend_compatibility.yaml",
        )
        telemetry_provider = self._build_telemetry_provider(config, telemetry_repository)
        model_management_service = ModelManagementService(
            registry=registry,
            model_server=model_server,
            compatibility_checker=compatibility_checker,
            lifecycle_manager=lifecycle_manager,
        )
        chat_service = ChatService(
            registry=registry,
            router=router,
            lifecycle_manager=lifecycle_manager,
            telemetry_provider=telemetry_provider,
            model_server=model_server,
        )
        health_service = HealthService(model_server=model_server, telemetry_provider=telemetry_provider)
        return PlatformApplication(
            config=config,
            registry=registry,
            router=router,
            lifecycle_manager=lifecycle_manager,
            telemetry_provider=telemetry_provider,
            compatibility_checker=compatibility_checker,
            model_server=model_server,
            plugin_manager=plugin_manager,
            model_management_service=model_management_service,
            chat_service=chat_service,
            health_service=health_service,
        )

    def create_fastapi_app(self, path: str | Path = "configs/platform.yaml") -> "FastAPI":
        """Build and return a FastAPI application for the given config file."""
        from llm_platform.gateway.app import create_app

        return create_app(self.build_from_file(path))

    def _build_plugins(self, config: PlatformConfig) -> PluginManager:
        """Load plugin implementations enabled in configuration."""
        available_plugins = {
            "qwen": QwenPlugin,
            "llama": LlamaPlugin,
            "mistral": MistralPlugin,
            "deepseek": DeepSeekPlugin,
        }
        plugin_manager = PluginManager()
        for plugin_id in config.plugins.enabled:
            plugin_class = available_plugins.get(plugin_id)
            if plugin_class:
                plugin_manager.register(plugin_class())
        return plugin_manager

    def _build_repositories(self, config: PlatformConfig):
        """Build repository implementations for the configured database."""
        engine = config.database.engine.lower()
        if engine == "memory":
            return (
                InMemoryModelRepository(),
                InMemoryDeploymentRepository(),
                InMemoryLifecycleRepository(),
                InMemoryTelemetryRepository(),
            )

        session_manager = DatabaseSessionManager(config.database)
        session_factory = session_manager.session_scope
        return (
            SQLAlchemyModelRepository(session_factory),
            SQLAlchemyDeploymentRepository(session_factory),
            SQLAlchemyLifecycleRepository(session_factory),
            SQLAlchemyTelemetryRepository(session_factory),
        )

    def _build_telemetry_provider(self, config: PlatformConfig, telemetry_repository) -> ITelemetryProvider:
        """Build the configured telemetry provider."""
        if config.telemetry.provider == "memory":
            return MemoryTelemetryProvider(telemetry_repository)
        if config.telemetry.provider == "database":
            return RepositoryTelemetryProvider(telemetry_repository)
        return NoOpTelemetryProvider()
