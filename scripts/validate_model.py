"""Inspect a Hugging Face model and emit a compatibility report."""

from __future__ import annotations

import argparse
import json

from llm_platform.compatibility.inspector import HuggingFaceModelInspector


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate a Hugging Face model for platform onboarding.")
    parser.add_argument("--hf-repo", required=True)
    parser.add_argument("--revision", default=None)
    parser.add_argument(
        "--compatibility-config",
        default="configs/validation/backend_compatibility.yaml",
    )
    return parser.parse_args()


def main() -> None:
    """Run the validation CLI."""
    args = parse_args()
    inspector = HuggingFaceModelInspector(args.compatibility_config)
    report = inspector.inspect(args.hf_repo, revision=args.revision)
    print(json.dumps(report.model_dump(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
