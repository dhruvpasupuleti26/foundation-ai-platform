"""Shared enumerations used across the platform."""

from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    CHAT = "chat"
    REASONING = "reasoning"
    TOOL_CALLING = "tool_calling"
    EMBEDDING = "embedding"
    EVALUATION = "evaluation"
    CLASSIFICATION = "classification"


class ModelStatus(StrEnum):
    REGISTERED = "registered"
    DEPLOYED = "deployed"
    DISABLED = "disabled"
    FAILED = "failed"


class DeploymentStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    UNLOADED = "unloaded"
    FAILED = "failed"


class LifecycleState(StrEnum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    FAILED = "FAILED"


class EngineType(StrEnum):
    VLLM = "vllm"
    HUGGINGFACE_TRANSFORMERS = "huggingface-transformers"
    TENSORRT_LLM = "tensorrt-llm"
    SGLANG = "sglang"
    TGI = "tgi"
    NIM = "nim"
    EXTERNAL_API = "external-api"
