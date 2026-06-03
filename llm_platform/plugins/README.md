# plugins

## Purpose

Load and register model family plugins without coupling the platform core to family names.

## Responsibilities

- Discover plugins
- Register capabilities and engines
- Isolate family-specific metadata

## Architecture

Plugins implement `IPlugin` and are loaded by a plugin manager. The platform core interacts only with interfaces and plugin manifests.

## Public APIs

- Plugin manager
- Plugin base classes

## Extension Points

- Entry-point based discovery
- Remote plugin manifests
- Organization-specific plugin packages

## Configuration Examples

- Enabled plugins in `configs/platform.yaml`

## Failure Modes

- Duplicate plugin identifiers
- Invalid manifests
- Version incompatibility between plugin and core

## Testing Strategy

- Plugin loading tests with synthetic plugins
