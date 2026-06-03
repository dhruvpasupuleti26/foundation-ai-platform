# integration tests

## Purpose

Validate subsystem composition with in-memory or lightweight dependencies.

## Responsibilities

- Exercise gateway-to-service wiring
- Validate repository and routing integration

## Architecture

Integration tests use real package wiring with fake servers and memory repositories.

## Public APIs

- `pytest tests/integration`

## Extension Points

- Temporary SQL backends

## Configuration Examples

- Test-specific dependency overrides

## Failure Modes

- Slow or flaky tests

## Testing Strategy

- Keep scope narrow and deterministic
