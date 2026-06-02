# services

## Purpose

Coordinate platform use cases without exposing transport or persistence details.

## Responsibilities

- Orchestrate registry, routing, lifecycle, and telemetry calls
- Provide clean entrypoints for the gateway
- Keep business logic testable

## Architecture

Services depend only on interfaces and schemas. They contain orchestration logic and return domain-friendly responses.

## Public APIs

- Model management service
- Chat service
- Health service

## Extension Points

- Authorization policies
- Workflow hooks
- Request enrichment

## Configuration Examples

- Service wiring is driven by `configs/platform.yaml`

## Failure Modes

- Downstream dependency failure
- Invalid orchestration sequences

## Testing Strategy

- Unit tests with fake implementations
