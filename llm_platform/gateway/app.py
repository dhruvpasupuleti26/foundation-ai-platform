"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from llm_platform.bootstrap import PlatformApplication
from llm_platform.gateway.routes import router


def create_app(platform_application: PlatformApplication) -> FastAPI:
    app = FastAPI(title="Foundation AI Platform")
    app.state.platform_application = platform_application
    app.include_router(router)
    return app
