# 01 System Overview

## Purpose

The Foundation AI Platform is a configuration-driven control plane and gateway for internal LLM serving. It is designed to host multiple model backends, register models and deployments, route requests by capability, manage deployment lifecycle, and emit telemetry without coupling the core platform to any model family.

## Core Design Decisions

- The platform routes by declared capability, not model-family name.
- Engine integration is abstracted behind `IModelServer`.
- Model-family integration is abstracted behind `IPlugin`.
- All externally relevant structures use validated Pydantic schemas.
- Business logic remains testable without GPUs through in-memory repositories and fake servers.

## Primary Subsystems

- `registry`: source of truth for models, deployments, and lifecycle state
- `plugins`: model-family extension boundary
- `serving`: engine abstraction boundary
- `routing`: capability-based selection
- `lifecycle`: state machine for deployment temperature
- `gateway`: HTTP entrypoint
- `telemetry`: metrics and tracing hooks
- `compatibility`: policy checks before deployment

## Near-Term Scope

The current scaffold intentionally stops short of real inference. It provides production-oriented structure, interfaces, test doubles, and gateway placeholders so subsequent phases can add implementation without reworking the architecture.
