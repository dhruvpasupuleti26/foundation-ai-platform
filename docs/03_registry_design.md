# 03 Registry Design

## Responsibilities

The registry tracks model metadata, deployment records, and lifecycle state. It is the control-plane source of truth consumed by routing, lifecycle, and gateway services.

## Core Interfaces

- `IRegistry`
- `IModelRepository`
- `IDeploymentRepository`
- `ILifecycleRepository`

## Data Model

### Model Table

- `id`
- `name`
- `version`
- `engine`
- `capabilities`
- `memory_requirements`
- `ownership`
- `status`
- `created_at`

### Deployment Table

- `deployment_id`
- `model_id`
- `endpoint`
- `status`
- `last_used`
- `created_at`

### Lifecycle Table

- `deployment_id`
- `state`
- `last_transition`
- `idle_duration`

## Implementation Strategy

- Use an in-memory repository for local development and tests.
- Introduce SQL-backed repositories later without changing service interfaces.
- Keep registry services small and orchestration-friendly.

## Failure Modes

- Missing records
- Duplicate logical registrations
- Stale deployment metadata
