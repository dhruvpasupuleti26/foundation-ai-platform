# 12 Testing Strategy

## Test Pyramid

- unit tests for core logic and interfaces
- integration tests for service and gateway composition
- e2e tests for deployed environments later

## Rules

- no GPU dependency in unit or integration tests
- use fake servers and memory repositories
- validate configs and schemas as first-class assets

## Initial Coverage

- config loading with env overrides
- plugin bootstrap
- lifecycle transitions
- routing selection
- model deployment orchestration
- gateway happy-path flow
