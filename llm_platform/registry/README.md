# registry

## Purpose

Track models, deployments, and their current operational metadata.

## Responsibilities

- Register models and versions
- Persist deployment records
- Support lookup for routing and lifecycle

## Architecture

Registry services depend on an abstract repository interface so storage can be in-memory for tests or SQL-backed in production.

## Public APIs

- Registry service
- Repository implementations

## Extension Points

- Alternate persistence backends
- Metadata enrichers
- Validation hooks

## Configuration Examples

- Database configuration in `configs/platform.yaml`

## Failure Modes

- Duplicate registrations
- Unknown model references
- Persistence outages

## Testing Strategy

- Unit tests with in-memory repositories
- Integration tests against temporary SQL backends later
