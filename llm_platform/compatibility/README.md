# compatibility

## Purpose

Validate whether a model, engine, hardware profile, and deployment request are compatible.

## Responsibilities

- Check engine support
- Validate capability declarations
- Reject unsupported deployment combinations

## Architecture

Compatibility checks are applied before deployment and plugin loading. The subsystem remains policy-driven and extensible.

## Public APIs

- Compatibility checker

## Extension Points

- GPU profile validation
- Quantization support rules
- Organization policy controls

## Configuration Examples

- Support matrices in `configs/deployments/`

## Failure Modes

- Invalid engine-model combination
- Missing capability metadata
- Unsupported memory profile

## Testing Strategy

- Rule evaluation tests using synthetic deployment requests
