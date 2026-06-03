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

The repository now also includes:

- a local `HuggingFaceModelServer` for CPU, MPS, and CUDA smoke tests
- a `VLLMModelServer` client that targets vLLM's OpenAI-compatible server
- a `TGIModelServer` client that targets TGI's OpenAI-compatible Messages API

## Production Direction

Real adapters should translate between engine-specific deployment semantics and platform schemas while preserving consistent error behavior.
