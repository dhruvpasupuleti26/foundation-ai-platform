# scripts

## Purpose

Operational and developer helper scripts for the platform.

## Responsibilities

- Bootstrap local development workflows
- Provide offline maintenance tooling

## Architecture

Scripts should remain thin wrappers around package APIs whenever possible.

## Public APIs

- None yet

## Extension Points

- Seeding registry data
- Running reconciliation jobs

## Configuration Examples

- Use `configs/` as script inputs

## Failure Modes

- Environment misconfiguration

## Testing Strategy

- Smoke tests for scripts as they are added
