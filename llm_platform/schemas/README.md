# schemas

## Purpose

Provide validated, serializable domain models for configuration, API, registry, routing, lifecycle, and telemetry.

## Responsibilities

- Validate external inputs
- Normalize internal data exchange
- Document the contract surface between layers

## Architecture

Schemas are Pydantic models shared across services, APIs, and repositories. They do not own persistence or business logic.

## Public APIs

- Configuration models
- Registry models
- Gateway request and response models
- Telemetry event models

## Extension Points

- Add future schemas for agents, fine-tuning, evaluations, and batch inference

## Configuration Examples

See `configs/` for YAML that maps directly into configuration schemas.

## Failure Modes

- Validation failures for malformed YAML or API payloads
- Version skew across producers and consumers

## Testing Strategy

- Unit tests for model validation and defaults
