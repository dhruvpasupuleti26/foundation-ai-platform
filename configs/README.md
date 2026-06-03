# configs

## Purpose

Store YAML configuration defaults and examples for the platform.

## Responsibilities

- Capture platform wiring without code changes
- Provide environment-portable examples
- Separate policy from implementation

## Architecture

Configuration files are organized by concern and loaded through the platform configuration loader with environment overrides.

## Public APIs

- YAML files consumed by `ConfigLoader`

## Extension Points

- Environment-specific overlays
- Secret management adapters

## Configuration Examples

- `platform.yaml`
- `models/catalog.yaml`
- `routing/routes.yaml`

## Failure Modes

- Missing required fields
- Contradictory overrides

## Testing Strategy

- Schema validation tests against sample configs
