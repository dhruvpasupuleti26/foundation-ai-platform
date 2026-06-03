# 06 Gateway Design

## Purpose

Expose a stable OpenAI-style internal API over platform services.

## Endpoints

- `POST /chat/completions`
- `POST /v1/chat/completions`
- `POST /models/register`
- `POST /models/validate`
- `POST /models/deploy`
- `POST /models/unload`
- `GET /models`
- `GET /v1/models`
- `GET /models/{id}`
- `GET /health`
- `GET /metrics`

## Design Rules

- Transport logic stays in FastAPI routers.
- Business logic stays in `services/`.
- Errors from domain services are translated to HTTP responses at the edge.

## Future Concerns

- Authentication and authorization
- Rate limiting and quotas
- Streaming responses
- Idempotency and request replay safety
