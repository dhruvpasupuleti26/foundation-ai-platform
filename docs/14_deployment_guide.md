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

## Local Multi-Service Stack

The repository now includes:

- `docker-compose.yml` with `gateway`, `vllm`, and `tgi` services
- `deployment/Dockerfile.gateway` for the gateway image
- `.env.example` for local environment values

Use CUDA-capable Linux hosts for the `vllm` and `tgi` compose profiles. Apple Silicon developers should continue using the local Transformers smoke-test path instead of the GPU compose stack.

## Operational Concerns

- configuration promotion across environments
- plugin rollout governance
- engine-specific node pools
