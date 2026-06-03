# serving

## Purpose

Abstract model server engines such as vLLM and HuggingFace Transformers.

## Responsibilities

- Define deployment and unload operations
- Surface health and capability information
- Hide engine-specific details from the rest of the platform

## Architecture

Serving implementations satisfy `IModelServer`. Plugins attach specific engine adapters without leaking model-family assumptions into the core.

## Public APIs

- Engine adapters
- Fake model server for tests
- HuggingFace local model server for smoke tests and developer workflows
- Placement resolution helpers

## Extension Points

- Add new engines such as TensorRT-LLM, TGI, SGLang, NIM, and external APIs
- Extend placement policies for fleet schedulers and node selectors

## Configuration Examples

- Engine settings under `configs/deployments/`
- Placement examples under `configs/deployments/placement_profiles.yaml`

## Failure Modes

- Deployment failures
- Engine health degradation
- Runtime incompatibilities

## Testing Strategy

- Unit tests with fake servers and no GPU dependency
- Optional smoke tests with the in-process HuggingFace backend on CPU, MPS, or CUDA hosts
