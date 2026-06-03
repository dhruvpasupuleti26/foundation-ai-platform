from __future__ import annotations

from fastapi.testclient import TestClient

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.database.models import Base
from llm_platform.database.session import DatabaseSessionManager
from llm_platform.gateway.app import create_app
from llm_platform.schemas.config import DatabaseConfig, PlatformConfig


def test_openai_chat_completions_route_returns_openai_shape(tmp_path):
    config = PlatformConfig(database=DatabaseConfig(engine="sqlite", path=str(tmp_path / "platform.db")))
    session_manager = DatabaseSessionManager(config.database)
    Base.metadata.create_all(session_manager.engine)
    client = TestClient(create_app(PlatformApplicationBuilder().build_from_config(config)))

    register = client.post(
        "/v1/models/register",
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
    model_id = register.json()["model"]["id"]
    client.post("/v1/models/deploy", json={"model_id": model_id, "endpoint": "http://localhost:8001", "engine": "vllm"})

    response = client.post(
        "/v1/chat/completions",
        json={"model": "chat-model", "messages": [{"role": "user", "content": "hello"}], "stream": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["role"] == "assistant"
