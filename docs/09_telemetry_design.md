# 09 Telemetry Design

## Captured Fields

- `request_id`
- `model`
- `latency`
- `prompt_tokens`
- `completion_tokens`
- `cache_hit`
- `error`
- `timestamps`

## Integration Points

- `ITelemetryProvider`
- Prometheus metrics export
- OpenTelemetry trace and span export

## Current Providers

- `MemoryTelemetryProvider`
- `NoOpTelemetryProvider`

## Design Guidance

- keep high-cardinality labels constrained
- separate business events from operational metrics
- avoid hard dependencies on a single observability vendor
