"""Gateway dependency helpers."""

from __future__ import annotations

from fastapi import Request

from llm_platform.bootstrap import PlatformApplication


def get_application(request: Request) -> PlatformApplication:
    return request.app.state.platform_application
