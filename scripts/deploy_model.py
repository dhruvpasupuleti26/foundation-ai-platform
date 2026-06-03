"""Deploy a registered model through the platform service layer."""

from __future__ import annotations

import argparse

from llm_platform.bootstrap import PlatformApplicationBuilder
from llm_platform.schemas.registry import DeploymentCreateRequest


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Deploy a registered model.")
    parser.add_argument("--config", default="configs/platform.yaml")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--engine", default=None)
    parser.add_argument("--placement", default=None)
    return parser.parse_args()


def main() -> None:
    """Run the deployment CLI."""
    args = parse_args()
    application = PlatformApplicationBuilder().build_from_file(args.config)
    deployment = application.model_management_service.deploy_model(
        DeploymentCreateRequest(
            model_id=args.model_id,
            endpoint=args.endpoint,
            engine=args.engine,
            placement=args.placement,
        )
    )
    print(f"deployed deployment_id={deployment.deployment_id} endpoint={deployment.endpoint}")


if __name__ == "__main__":
    main()
