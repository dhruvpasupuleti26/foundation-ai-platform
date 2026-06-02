"""YAML configuration loading with environment overrides."""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class ConfigLoader:
    """Load configuration from YAML and environment variables."""

    def __init__(self, env_prefix: str = "LLM_PLATFORM") -> None:
        self._env_prefix = env_prefix

    def load(self, path: str | Path, model_type: type[T]) -> T:
        base_data = self._read_yaml(path)
        merged = self._merge_dicts(base_data, self._read_environment())
        return model_type.model_validate(merged)

    def _read_yaml(self, path: str | Path) -> dict[str, Any]:
        candidate = Path(path)
        if not candidate.exists():
            return {}
        with candidate.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _read_environment(self) -> dict[str, Any]:
        nested: dict[str, Any] = {}
        prefix = f"{self._env_prefix}__"
        for key, raw_value in os.environ.items():
            if not key.startswith(prefix):
                continue
            parts = key[len(prefix) :].lower().split("__")
            current = nested
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = yaml.safe_load(raw_value)
        return nested

    def _merge_dicts(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result = deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
