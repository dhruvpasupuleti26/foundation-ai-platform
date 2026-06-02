from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.database.models import Base
from llm_platform.database.session import DatabaseSessionManager
from llm_platform.gateway.app import create_app
from llm_platform.schemas.config import DatabaseConfig, PlatformConfig


def test_gateway_register_deploy_and_chat_flow(tmp_path):
    database_path = tmp_path / "platform.db"
    config = PlatformConfig(database=DatabaseConfig(engine="sqlite", path=str(database_path)))
    session_manager = DatabaseSessionManager(config.database)
    Base.metadata.create_all(session_manager.engine)
    app = create_app(PlatformApplicationBuilder().build_from_config(config))
    client = TestClient(app)

    register_response = client.post(
        "/models/register",
        json={
            "name": "chat-model",
            "version": "1.0.0",
            "family": "qwen",
            "engine": "vllm",
            "capabilities": ["chat"],
            "memory_requirement_gb": 24,
            "ownership": "platform",
        },
    )
    assert register_response.status_code == 201
    model_id = register_response.json()["model"]["id"]

    deploy_response = client.post(
        "/models/deploy",
        json={"model_id": model_id, "endpoint": "http://localhost:8001", "engine": "vllm"},
    )
    assert deploy_response.status_code == 201

    chat_response = client.post(
        "/chat/completions",
        json={"capability": "chat", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert chat_response.status_code == 200
    assert chat_response.json()["status"] == "accepted"
    assert Path(database_path).exists()
