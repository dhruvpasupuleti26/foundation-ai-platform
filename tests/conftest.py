from __future__ import annotations

from fastapi.testclient import TestClient

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.database.models import Base
from llm_platform.database.session import DatabaseSessionManager
from llm_platform.gateway.app import create_app
from llm_platform.schemas.config import DatabaseConfig, PlatformConfig


def build_test_client() -> TestClient:
    config = PlatformConfig(database=DatabaseConfig(engine="sqlite", path="./data/test-platform.db"))
    session_manager = DatabaseSessionManager(config.database)
    Base.metadata.create_all(session_manager.engine)
    application = PlatformApplicationBuilder().build_from_config(config)
    return TestClient(create_app(application))
