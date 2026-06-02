# 14 Deployment Guide

## Current Local Workflow

1. Install the package with development dependencies.
2. Run `make init` or `python scripts/bootstrap.py`.
3. The bootstrap step creates the SQLite database, applies Alembic migrations, and loads sample data.
4. Build the FastAPI app through `PlatformApplicationBuilder`.
5. Run the gateway with `uvicorn`.

## Packaging Direction

- container image for gateway
- separate worker processes for lifecycle reconciliation
- external database for registry persistence
- Prometheus and OpenTelemetry collectors

## Operational Concerns

- configuration promotion across environments
- plugin rollout governance
- engine-specific node pools
