# tests

## Purpose

Contain automated validation for platform behavior.

## Responsibilities

- Unit-test business logic without GPUs
- Exercise subsystem integration with fakes and in-memory repositories
- Reserve e2e coverage for later deployment validation

## Architecture

Tests are split by scope into unit, integration, and e2e directories.

## Public APIs

- `pytest`

## Extension Points

- Contract test suites for plugins and engines
- Fixture libraries for deployment scenarios

## Configuration Examples

- Run `pytest`

## Failure Modes

- Over-reliance on integration coverage
- Tests coupled to implementation details

## Testing Strategy

- Prefer unit tests with fake implementations
