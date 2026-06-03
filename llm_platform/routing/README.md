# routing

## Purpose

Route requests to compatible deployments based on declared capabilities rather than model names.

## Responsibilities

- Match requested capabilities to eligible models
- Apply policy-based selection
- Return deterministic routing decisions when possible

## Architecture

Routing depends on registry read models plus configurable rules. It does not know about family names such as Qwen or Llama.

## Public APIs

- Router
- Route policy evaluator

## Extension Points

- Cost-aware routing
- Multi-objective ranking
- A/B or canary routing

## Configuration Examples

- Rules in `configs/routing/routes.yaml`

## Failure Modes

- No eligible model found
- Ambiguous selections without ranking policy
- Stale registry data

## Testing Strategy

- Unit tests with fake registry snapshots
