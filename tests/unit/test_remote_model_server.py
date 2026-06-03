from __future__ import annotations

import httpx

from llm_platform.schemas.config import OpenAICompatibleBackendConfig
from llm_platform.schemas.gateway import ChatCompletionRequest, ChatMessage
from llm_platform.schemas.registry import DeploymentCreateRequest, ModelRecord
from llm_platform.serving.tgi_client import TGIModelServer
from llm_platform.serving.vllm_client import VLLMModelServer


def test_vllm_remote_model_server_deploy_and_generate(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok from vllm"}}]},
            )
        raise AssertionError(f"Unexpected path: {request.url.path}")

    server = VLLMModelServer(OpenAICompatibleBackendConfig(base_url="http://example.test"))
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(server, "_client", lambda base_url: httpx.Client(base_url=base_url, transport=transport))
    model = ModelRecord(
        id="model-1",
        name="tool-caller",
        version="1.0.0",
        family="qwen",
        engine="vllm",
        capabilities=["chat"],
        memory_requirement_gb=8,
        ownership="platform",
        metadata={"remote_model_name": "Qwen/Qwen2.5-7B-Instruct"},
    )
    deployment = server.deploy(model, DeploymentCreateRequest(model_id=model.id, endpoint="http://example.test"))
    message = server.generate(
        deployment,
        ChatCompletionRequest(messages=[ChatMessage(role="user", content="hello")]),
    )

    assert deployment.metadata["implementation"] == "vllm-openai"
    assert message == "ok from vllm"


def test_tgi_remote_model_server_uses_openai_compatible_response(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/v1/chat/completions":
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok from tgi"}}]},
            )
        raise AssertionError(f"Unexpected path: {request.url.path}")

    server = TGIModelServer(OpenAICompatibleBackendConfig(base_url="http://example.test"))
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(server, "_client", lambda base_url: httpx.Client(base_url=base_url, transport=transport))
    model = ModelRecord(
        id="model-2",
        name="response-model",
        version="1.0.0",
        family="mistral",
        engine="tgi",
        capabilities=["chat"],
        memory_requirement_gb=8,
        ownership="platform",
        metadata={"remote_model_name": "tgi"},
    )
    deployment = server.deploy(model, DeploymentCreateRequest(model_id=model.id, endpoint="http://example.test"))
    message = server.generate(
        deployment,
        ChatCompletionRequest(messages=[ChatMessage(role="user", content="hello")], temperature=0.0),
    )

    assert deployment.metadata["implementation"] == "tgi-messages-api"
    assert message == "ok from tgi"
