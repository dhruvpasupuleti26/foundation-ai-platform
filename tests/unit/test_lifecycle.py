from __future__ import annotations

from llm_platform.lifecycle.manager import SimpleLifecycleManager
from llm_platform.schemas.enums import LifecycleState
from llm_platform.schemas.registry import DeploymentRecord, LifecycleRecord


def test_lifecycle_manager_reconciles_to_warm_and_cold():
    manager = SimpleLifecycleManager(warm_after_seconds=10, cold_after_seconds=20)
    deployment = DeploymentRecord(model_id="model-1", endpoint="http://localhost", engine="vllm")
    record = manager.initialize(deployment)

    warm_record = manager.reconcile(record.model_copy(update={"idle_duration_seconds": 15}))
    cold_record = manager.reconcile(record.model_copy(update={"idle_duration_seconds": 25}))

    assert warm_record.state == LifecycleState.WARM
    assert cold_record.state == LifecycleState.COLD
