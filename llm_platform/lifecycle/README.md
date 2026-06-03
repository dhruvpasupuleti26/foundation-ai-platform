# lifecycle

## Purpose

Manage deployment temperature state transitions such as `HOT`, `WARM`, `COLD`, and `FAILED`.

## Responsibilities

- Apply lifecycle policy rules
- Track state transitions
- Coordinate unload and warmup behavior

## Architecture

Lifecycle services consult registry state, deployment metadata, and policies from configuration. They avoid direct dependency on concrete serving engines.

## Public APIs

- Lifecycle manager
- Lifecycle policy evaluator

## Extension Points

- New transition guards
- Cost-based or SLA-based policies
- Scheduled reconciliation loops

## Configuration Examples

- Policies in `configs/lifecycle/policies.yaml`

## Failure Modes

- Illegal state transitions
- Missing deployment metadata
- Serving backend unavailability during transition

## Testing Strategy

- Unit tests for transition policy evaluation
