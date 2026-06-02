# e2e tests

## Purpose

Reserve space for deployment-level validation once real serving backends are introduced.

## Responsibilities

- Validate production-like workflows end to end

## Architecture

These tests will eventually run against deployed gateway, registry, and serving infrastructure.

## Public APIs

- `pytest tests/e2e`

## Extension Points

- Staging environment smoke tests

## Configuration Examples

- Environment-driven test targets

## Failure Modes

- Environmental flakiness

## Testing Strategy

- Keep e2e coverage selective
