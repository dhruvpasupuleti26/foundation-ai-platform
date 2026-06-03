# 11 Configuration System

## Principles

- YAML is the primary source of truth
- environment variables override YAML
- Pydantic validates the final merged shape
- defaults live in configuration schemas

## Environment Override Convention

Use double underscores to express nesting.

Example:

`LLM_PLATFORM__GATEWAY__PORT=9000`

## Current Scope

- platform metadata
- gateway settings
- database engine, path, host, port, and generated SQLAlchemy URL
- enabled plugins
- serving engines
- telemetry provider settings

## Future Scope

- lifecycle policies
- routing policies
- registry persistence strategy
- authn/authz
