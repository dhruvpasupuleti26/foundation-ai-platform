"""Smoke test a real local hosting path with the platform service layer.

This script registers a model, deploys it through the configured HuggingFace
backend, runs a single chat completion, and unloads the deployment again. It is
intended for developer validation on CPU, CUDA, or Apple Metal MPS hosts.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.database.models import Base
from llm_platform.database.session import DatabaseSessionManager
from llm_platform.schemas.config import DatabaseConfig, PlatformConfig, ServingConfig
from llm_platform.schemas.gateway import ChatCompletionRequest, ChatMessage
from llm_platform.schemas.registry import DeploymentCreateRequest, ModelRegistrationRequest


def build_config(database_path: Path, placement: str) -> PlatformConfig:
    """Build a runtime config suitable for local smoke testing.

    Args:
        database_path: SQLite database path for the smoke test.
        placement: Preferred placement to request for deployment.

    Returns:
        Platform configuration targeting the local Transformers backend.
    """
    return PlatformConfig(
        database=DatabaseConfig(engine="sqlite", path=str(database_path)),
        serving=ServingConfig(
            implementation="huggingface-transformers",
            default_engine="huggingface-transformers",
            supported_engines=["huggingface-transformers"],
            default_placement=placement,
            fallback_placements=["cpu"] if placement != "cpu" else [],
            model_cache_dir="./data/model-cache",
        ),
    )


def run_smoke_test(model_source_id: str, placement: str) -> str:
    """Run an end-to-end hosting smoke test.

    Args:
        model_source_id: Upstream model identifier passed to
            `transformers.from_pretrained`.
        placement: Preferred runtime placement such as `mps`, `cuda`, or
            `cpu`.

    Returns:
        Generated model response text.
    """
    config = build_config(Path("./data/qwen3-smoke.db"), placement)
    session_manager = DatabaseSessionManager(config.database)
    Base.metadata.create_all(session_manager.engine)
    application = PlatformApplicationBuilder().build_from_config(config)
    model = application.model_management_service.register_model(
        ModelRegistrationRequest(
            name="local-qwen3-smoke",
            version="1.0.0",
            family="qwen",
            engine="huggingface-transformers",
            capabilities=["chat", "reasoning"],
            memory_requirement_gb=8,
            ownership="platform",
            metadata={"source_model_id": model_source_id},
        )
    )
    deployment = application.model_management_service.deploy_model(
        DeploymentCreateRequest(
            model_id=model.id,
            endpoint=f"local://{model.name}",
            engine="huggingface-transformers",
            placement=placement,
            fallback_placements=["cpu"] if placement != "cpu" else [],
        )
    )
    try:
        response = application.chat_service.create_completion(
            ChatCompletionRequest(
                messages=[
                    ChatMessage(
                        role="user",
                        content="Reply in one short sentence and include the exact phrase: smoke test passed.",
                    )
                ],
                metadata={"max_new_tokens": 48, "do_sample": False, "enable_thinking": False},
            )
        )
        return response.message
    finally:
        application.model_management_service.unload_model(deployment.deployment_id)


def parse_args() -> argparse.Namespace:
    """Parse script arguments."""
    parser = argparse.ArgumentParser(description="Run a local hosting smoke test.")
    parser.add_argument("--model-source-id", default="Qwen/Qwen3-1.7B")
    parser.add_argument("--placement", default="mps", choices=["cpu", "mps", "cuda"])
    return parser.parse_args()


def main() -> None:
    """Run the command-line entrypoint."""
    args = parse_args()
    message = run_smoke_test(args.model_source_id, args.placement)
    print(message)


if __name__ == "__main__":
    main()
