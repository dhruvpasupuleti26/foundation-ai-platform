"""Register a model from a YAML document into the platform registry."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.schemas.registry import ModelRegistrationRequest


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Register a model YAML into the platform registry.")
    parser.add_argument("--config", default="configs/platform.yaml")
    parser.add_argument("--model-yaml", required=True)
    return parser.parse_args()


def main() -> None:
    """Run the registration CLI."""
    args = parse_args()
    application = PlatformApplicationBuilder().build_from_file(args.config)
    with Path(args.model_yaml).open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    models = payload["models"] if "models" in payload else [payload]
    for item in models:
        model = application.model_management_service.register_model(ModelRegistrationRequest(**item))
        print(f"registered model_id={model.id} name={model.name} engine={model.engine}")


if __name__ == "__main__":
    main()
