# `docs/` — Architecture & Design Documentation

Comprehensive design documents covering the platform's architecture, subsystem designs, and operational guides. Read these documents in order for a full understanding of the system.

---

## Document Index

| # | File | Topic |
|---|---|---|
| 01 | `01_system_overview.md` | High-level system overview, goals, and architecture principles. |
| 02 | `02_project_structure.md` | Repository layout, package organization, and module dependency rules. |
| 03 | `03_registry_design.md` | Model and deployment registry design — schemas, persistence, and service boundaries. |
| 04 | `04_plugin_architecture.md` | Plugin system design — manifest schema, registration, and extensibility. |
| 05 | `05_serving_architecture.md` | Serving backend architecture — factory pattern, backend adapters, and placement resolution. |
| 06 | `06_gateway_design.md` | FastAPI gateway design — routing, dependency injection, and OpenAI compatibility. |
| 07 | `07_routing_design.md` | Capability-based routing design — selection algorithm and route decision model. |
| 08 | `08_lifecycle_design.md` | Deployment lifecycle state machine — thermal states, idle timeouts, and reconciliation. |
| 09 | `09_telemetry_design.md` | Telemetry system design — event model, provider abstraction, and metrics snapshots. |
| 10 | `10_database_design.md` | Database design — ORM models, repository pattern, session management, and migration strategy. |
| 11 | `11_configuration_system.md` | Configuration system — YAML loading, environment overrides, and Pydantic validation. |
| 12 | `12_testing_strategy.md` | Testing strategy — unit/integration/E2E test organization and fixture patterns. |
| 13 | `13_security_guidelines.md` | Security guidelines — authentication, authorization, and secrets management. |
| 14 | `14_deployment_guide.md` | Deployment guide — Docker setup, docker-compose orchestration, and production considerations. |
| 15 | `15_future_agent_architecture.md` | Future agent architecture — planned agentic capabilities and extension points. |
| 16 | `16_hosting_and_placements.md` | Hosting and placement guide — CPU/CUDA/MPS support, placement resolution, and hardware requirements. |
