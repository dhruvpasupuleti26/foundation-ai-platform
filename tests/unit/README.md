# unit tests

## Purpose

Validate isolated business logic with fake dependencies.

## Responsibilities

- Cover routing, lifecycle, config loading, plugins, and services

## Architecture

Unit tests should avoid network, database, and GPU requirements.

## Public APIs

- `pytest tests/unit`

## Extension Points

- Shared fixtures

## Configuration Examples

- In-memory configs and repositories

## Failure Modes

- Hidden integration assumptions

## Testing Strategy

- Fast deterministic tests
