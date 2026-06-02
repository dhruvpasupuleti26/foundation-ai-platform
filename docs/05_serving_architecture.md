# 05 Serving Architecture

## Objective

Abstract serving backends so the rest of the platform can deploy and unload models without backend-specific coupling.

## Primary Interface

- `IModelServer`

## Initial Backends

- vLLM
- HuggingFace Transformers

## Future Backends

- TensorRT-LLM
- SGLang
- TGI
- NIM
- External APIs

## Current Scaffold

`FakeModelServer` provides deploy, unload, health, and placeholder generation behavior so orchestration can be tested before inference exists.

## Production Direction

Real adapters should translate between engine-specific deployment semantics and platform schemas while preserving consistent error behavior.
