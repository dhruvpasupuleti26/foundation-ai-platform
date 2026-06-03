"""Validation and compatibility report schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ValidationReport(BaseModel):
    """Compatibility and onboarding report for a model candidate."""

    hf_repo: str
    revision: str | None = None
    architecture: str | None = None
    tokenizer_status: str
    chat_template_status: str
    config_status: str
    compatibility: str
    recommended_backend: str
    estimated_gpu_memory_gb: float | None = None
    max_context_length: int | None = None
    smoke_test_status: str = "not_run"
    json_validity_status: str = "not_run"
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
