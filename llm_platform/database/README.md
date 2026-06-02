# database

## Purpose

Define storage-oriented models and database abstractions for registry data.

## Responsibilities

- Represent tables and persistence mappings
- Contain repository implementations
- Isolate persistence from business services
- Own SQLAlchemy session management and Alembic migration integration

## Architecture

Services depend on repository interfaces, not on SQLAlchemy directly. SQLAlchemy ORM is the only persistence implementation in the initial platform, with SQLite as the default backend and room for PostgreSQL or MySQL through configuration changes.

## Public APIs

- ORM models
- SQLAlchemy repositories
- In-memory repositories
- Session manager

## Extension Points

- PostgreSQL-specific tuning
- Alembic migrations
- Read/write split repositories

## Configuration Examples

- Structured database configuration in `configs/platform.yaml`

## Failure Modes

- Connection failures
- Schema drift
- Serialization mismatches

## Testing Strategy

- Unit tests with in-memory repositories
- Integration tests for SQLAlchemy repositories with temporary SQLite databases
