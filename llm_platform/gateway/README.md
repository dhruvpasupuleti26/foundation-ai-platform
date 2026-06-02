# gateway

## Purpose

Expose the platform through a stable HTTP API.

## Responsibilities

- Define API routes and request/response contracts
- Delegate work to services
- Avoid embedding business logic in controllers

## Architecture

The gateway uses FastAPI routers backed by service interfaces. Transport concerns stay here; orchestration lives in `services`.

## Public APIs

- `create_app()`
- API routers under `/chat`, `/models`, `/health`, and `/metrics`

## Extension Points

- Authentication middleware
- Rate limiting
- Request validation and tracing policies

## Configuration Examples

- Host, port, and metrics settings from `configs/platform.yaml`

## Failure Modes

- Invalid request payloads
- Downstream service failures
- Misconfigured dependency wiring

## Testing Strategy

- API tests with FastAPI `TestClient`
- Dependency override tests with in-memory services
