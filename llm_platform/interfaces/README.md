# interfaces

## Purpose

Declare subsystem contracts that implementations must satisfy.

## Responsibilities

- Define abstract interfaces
- Support dependency inversion
- Keep core services decoupled from implementations

## Architecture

Interfaces are grouped by capability rather than by implementation detail. Concrete classes in other packages depend on these contracts instead of each other.

## Public APIs

- `IModelServer`
- `IRegistry`
- `IRouter`
- `ILifecycleManager`
- `ITelemetryProvider`
- `ICompatibilityChecker`
- `IPlugin`
- `IModelRepository`
- `IDeploymentRepository`
- `ILifecycleRepository`
- `ITelemetryRepository`

## Extension Points

- Add new subsystem contracts for future capabilities such as fine-tuning and agents

## Configuration Examples

Interface selection is controlled by runtime wiring in `configs/platform.yaml`.

## Failure Modes

- Partial implementations that violate the interface contract
- Incompatible return shapes between interface and schema layers

## Testing Strategy

- Contract tests against fake and in-memory implementations
