# 10 Database Design

## Approach

The database layer defines persistence structure without forcing the platform to use a database during tests.

## Current Components

- SQLAlchemy declarative models for registry tables
- repository interfaces per aggregate
- SQLAlchemy repository implementations for models, deployments, lifecycle, and telemetry
- SQLite as the default backend
- Alembic migrations for schema management

## Planned Additions

- PostgreSQL repository implementation
- transactional write model
- read model projections for routing

## Design Tradeoff

The platform uses SQLAlchemy ORM repositories now so local development matches the production data path, while in-memory repositories remain available only for unit tests. Service-layer code stays unchanged if the configured database moves from SQLite to PostgreSQL, MySQL, CloudSQL, or Aurora.
