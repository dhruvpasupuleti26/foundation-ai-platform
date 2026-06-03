# 08 Lifecycle Design

## States

- `HOT`
- `WARM`
- `COLD`
- `FAILED`

## Intent

Lifecycle state expresses deployment readiness and cost posture. Routing can prefer active deployments while reconciliation policies can cool idle ones.

## Current Policy

- `HOT` after recent use
- `WARM` after the warm threshold
- `COLD` after the cold threshold
- `FAILED` reserved for backend or policy failures

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> HOT
    HOT --> WARM: idle threshold reached
    WARM --> COLD: idle threshold reached
    HOT --> FAILED: deployment failure
    WARM --> FAILED: deployment failure
    COLD --> HOT: traffic or warmup
    COLD --> FAILED: deployment failure
```

## Future Work

- background reconciliation loop
- scheduled warm pools
- tenant-specific lifecycle policy
