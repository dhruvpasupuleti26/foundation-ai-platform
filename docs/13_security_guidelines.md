# 13 Security Guidelines

## Baseline Rules

- treat model registration and deployment endpoints as privileged
- separate operational auth from inference auth
- never trust client-supplied model metadata without validation
- keep secrets out of YAML defaults

## Future Controls

- service-to-service authentication
- audit logging
- RBAC for model registration and deployment
- request payload redaction in telemetry
- policy enforcement for external model connectors
