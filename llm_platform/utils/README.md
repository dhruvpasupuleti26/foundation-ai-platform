# utils

## Purpose

Provide small reusable helpers shared across subsystems.

## Responsibilities

- Configuration loading
- Environment override parsing
- Common error helpers

## Architecture

Utilities stay intentionally narrow to avoid becoming a dumping ground. Domain logic belongs in subsystem packages.

## Public APIs

- Configuration loader

## Extension Points

- Additional file loaders
- Safe merge utilities

## Configuration Examples

- `configs/platform.yaml`

## Failure Modes

- Invalid file paths
- Unsupported configuration shapes

## Testing Strategy

- Unit tests for parsing and merge behavior
