# 02 Project Structure

## Layout

- `llm_platform/`: Python package containing runtime code
- `configs/`: YAML defaults and examples
- `docs/`: design records and operational guidance
- `tests/`: automated validation
- `scripts/`: operator and developer automation
- `deployment/`: environment and packaging assets

## Package Organization

- `interfaces/`: abstract contracts
- `schemas/`: validated data models
- `registry/`: model and deployment registry service
- `plugins/`: family-specific plugin manifests
- `serving/`: backend serving adapters
- `routing/`: routing policies and selection logic
- `lifecycle/`: lifecycle state management
- `compatibility/`: deployment eligibility rules
- `telemetry/`: metrics and tracing providers
- `gateway/`: FastAPI transport layer
- `services/`: application use-case orchestration
- `database/`: persistence models and repositories
- `utils/`: narrow shared helpers

## Structural Rationale

The repository separates runtime code from operational assets and keeps each subsystem independently testable. Cross-package dependencies are expected to flow through `interfaces` and `schemas`, not directly through concrete implementations.
