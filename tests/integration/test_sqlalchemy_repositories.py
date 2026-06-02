from __future__ import annotations

from datetime import datetime, timezone

from llm_platform.database.models import Base
from llm_platform.database.repositories import (
    SQLAlchemyDeploymentRepository,
    SQLAlchemyLifecycleRepository,
    SQLAlchemyModelRepository,
    SQLAlchemyTelemetryRepository,
)
from llm_platform.database.session import DatabaseSessionManager
from llm_platform.schemas.config import DatabaseConfig
from llm_platform.schemas.enums import Capability, DeploymentStatus, LifecycleState
from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord, ModelRecord
from llm_platform.schemas.telemetry import TelemetryEvent


def test_sqlalchemy_repositories_roundtrip(tmp_path):
    config = DatabaseConfig(engine="sqlite", path=str(tmp_path / "repos.db"))
    session_manager = DatabaseSessionManager(config)
    Base.metadata.create_all(session_manager.engine)
    session_factory = session_manager.session_scope

    model_repository = SQLAlchemyModelRepository(session_factory)
    deployment_repository = SQLAlchemyDeploymentRepository(session_factory)
    lifecycle_repository = SQLAlchemyLifecycleRepository(session_factory)
    telemetry_repository = SQLAlchemyTelemetryRepository(session_factory)

    model = model_repository.save(
        ModelRecord(
            id="model-1",
            name="chat-model",
            version="1.0.0",
            family="qwen",
            engine="vllm",
            capabilities=[Capability.CHAT],
            memory_requirement_gb=24,
            ownership="platform",
        )
    )
    deployment = deployment_repository.save(
        DeploymentRecord(
            deployment_id="dep-1",
            model_id=model.id,
            endpoint="http://localhost:8001",
            engine="vllm",
            status=DeploymentStatus.READY,
        )
    )
    lifecycle_repository.save(
        LifecycleRecord(
            deployment_id=deployment.deployment_id,
            state=LifecycleState.HOT,
            idle_duration_seconds=0,
        )
    )
    telemetry_repository.save(
        TelemetryEvent(
            request_id="req-1",
            deployment_id=deployment.deployment_id,
            model_name=model.name,
            latency_ms=12.5,
            prompt_tokens=10,
            completion_tokens=5,
            cache_hit=False,
            error=None,
            timestamp=datetime.now(timezone.utc),
        )
    )

    assert model_repository.get("model-1").name == "chat-model"
    assert deployment_repository.get("dep-1").status == DeploymentStatus.READY
    assert lifecycle_repository.get("dep-1").state == LifecycleState.HOT
    assert telemetry_repository.snapshot().total_requests == 1
