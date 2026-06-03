# 07 Routing Design

## Core Principle

Requests route by capability and deployment health, not by model family name.

## Inputs

- Requested capability
- Registry model catalog
- Deployment readiness
- Lifecycle state

## Current Strategy

`CapabilityRouter` performs deterministic first-match selection over:

1. models that declare the capability
2. deployments in `READY`
3. lifecycle records not in `FAILED`

## Future Strategies

- weighted cost-aware routing
- latency-aware routing
- SLA-based routing
- canary and A/B routing
- tenant-scoped routing policies
