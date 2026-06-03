"""Fake serving implementation for tests and placeholder flows.

The fake server allows the service layer and gateway to exercise deployment and
request orchestration without importing heavyweight ML dependencies or
requiring GPU-capable hardware. It should remain deterministic and cheap.
"""

from __future__ import annotations

from llm_platform.interfaces.model_server import IModelServer
from llm_platform.schemas.gateway import ChatCompletionRequest
from llm_platform.schemas.registry import DeploymentCreateRequest, DeploymentRecord, ModelRecord


class FakeModelServer(IModelServer):
    """Non-GPU serving stub used until real engine adapters are implemented."""

    def deploy(self, model: ModelRecord, request: DeploymentCreateRequest) -> DeploymentRecord:
        """Create a synthetic deployment record.

        Args:
            model: Registered model metadata.
            request: Deployment request submitted by the service layer.

        Returns:
            A deployment record marked as ready with placeholder metadata.
        """
        return DeploymentRecord(
            model_id=model.id,
            endpoint=request.endpoint,
            engine=request.engine or model.engine,
            status="ready",
            metadata={"placeholder": "deployment created by fake server", **request.metadata},
        )

    def unload(self, deployment_id: str) -> None:
        """Unload a deployment.

        Args:
            deployment_id: Identifier of the deployment to unload.
        """
        del deployment_id

    def health(self) -> dict[str, str | list[str]]:
        """Return health metadata for the fake backend."""
        return {"status": "ok", "backend": "fake-model-server", "placements": ["cpu"]}

    def generate(self, deployment: DeploymentRecord, request: ChatCompletionRequest) -> str:
        """Return a deterministic placeholder response.

        Args:
            deployment: Deployment selected by routing.
            request: Chat completion request to acknowledge.

        Returns:
            Placeholder text describing which deployment would have handled the
            request.
        """
        return (
            "Inference is not implemented in this phase. "
            f"Request {request.request_id} would be served by deployment {deployment.deployment_id}."
        )
