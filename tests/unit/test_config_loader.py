from __future__ import annotations

import os

from llm_platform.schemas.config import DatabaseConfig, PlatformConfig
from llm_platform.utils.config_loader import ConfigLoader


def test_config_loader_applies_environment_override(monkeypatch, tmp_path):
    config_file = tmp_path / "platform.yaml"
    config_file.write_text("gateway:\n  port: 8000\n", encoding="utf-8")
    monkeypatch.setenv("LLM_PLATFORM__GATEWAY__PORT", "9100")

    config = ConfigLoader().load(config_file, PlatformConfig)

    assert config.gateway.port == 9100
    assert os.environ["LLM_PLATFORM__GATEWAY__PORT"] == "9100"


def test_database_config_builds_sqlite_and_postgres_urls():
    sqlite = DatabaseConfig(engine="sqlite", path="./data/platform.db")
    postgres = DatabaseConfig(
        engine="postgres",
        host="localhost",
        port=5432,
        database="llm_platform",
        username="user",
        password="secret",
    )

    assert sqlite.sqlalchemy_url.endswith("/data/platform.db")
    assert postgres.sqlalchemy_url == "postgresql+psycopg://user:secret@localhost:5432/llm_platform"
