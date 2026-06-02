# 15 Future Agent Architecture

## Why This Matters

Agent workflows will require more than chat completions. They need tool routing, memory policy, workflow state, and multi-step orchestration.

## Extension Points Already Present

- capability-based routing can expand to `tool_calling`
- plugin manifests can advertise agent-oriented capabilities
- telemetry interfaces can capture step-level events
- service boundaries can host orchestrators without changing the gateway contract

## Likely Future Subsystems

- agent runtime
- tool registry
- workflow state store
- conversation memory manager
- evaluation and safety policy engine

## Architectural Guidance

Keep agents as a separate orchestration layer above the serving plane. The LLM platform should remain the reusable inference, registry, routing, and telemetry foundation.
