"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from llm_platform.bootstrap import PlatformApplication, PlatformApplicationBuilder
from llm_platform.gateway.routes import router, v1_router


def create_app(platform_application: PlatformApplication) -> FastAPI:
    app = FastAPI(title="Foundation AI Platform")
    app.state.platform_application = platform_application
    app.include_router(router)
    app.include_router(v1_router)
    return app


def create_default_app() -> FastAPI:
    """Build the default FastAPI app from `configs/platform.yaml`."""
    return PlatformApplicationBuilder().create_fastapi_app("configs/platform.yaml")
