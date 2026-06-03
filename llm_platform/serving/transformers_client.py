"""Transformers local serving client alias.

This module exists to align the repository layout with the implementation plan,
which expects a dedicated transformers client module. The actual local runtime
implementation lives in `huggingface_model_server.py`.
"""

from __future__ import annotations

from llm_platform.serving.huggingface_model_server import HuggingFaceModelServer

__all__ = ["HuggingFaceModelServer"]
