"""Fake serving implementation for tests and placeholder flows."""

from __future__ import annotations

from llm_platform.interfaces.model_server import IModelServer
from llm_platform.schemas.gateway import ChatCompletionRequest
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord


class FakeModelServer(IModelServer):
    """Non-GPU serving stub used until real engine adapters are implemented."""

    def deploy(self, model: ModelRecord, request: DeploymentCreateRequest) -> DeploymentRecord:
        return DeploymentRecord(
            model_id=model.id,
            endpoint=request.endpoint,
            engine=request.engine or model.engine,
            status="ready",
            metadata={"placeholder": "deployment created by fake server", **request.metadata},
        )

    def unload(self, deployment_id: str) -> None:
        del deployment_id

    def health(self) -> dict[str, str]:
        return {"status": "ok", "backend": "fake-model-server"}

    def generate_placeholder(self, deployment: DeploymentRecord, request: ChatCompletionRequest) -> str:
        return (
            "Inference is not implemented in this phase. "
            f"Request {request.request_id} would be served by deployment {deployment.deployment_id}."
        )
