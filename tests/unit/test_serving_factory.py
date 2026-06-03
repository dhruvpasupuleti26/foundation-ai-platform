from __future__ import annotations

from llm_platform.schemas.config import PlatformConfig, ServingConfig
from llm_platform.serving.factory import build_model_server
from llm_platform.serving.fake_model_server import FakeModelServer
from llm_platform.serving.huggingface_model_server import HuggingFaceModelServer


def test_build_model_server_returns_fake_backend_by_default():
    server = build_model_server(PlatformConfig().serving)

    assert isinstance(server, FakeModelServer)


def test_build_model_server_returns_huggingface_backend_when_requested():
    server = build_model_server(ServingConfig(implementation="huggingface-transformers"))

    assert isinstance(server, HuggingFaceModelServer)
