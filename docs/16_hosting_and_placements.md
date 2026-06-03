# 16 Hosting And Placements

## Purpose

This document describes the first real local hosting path added to the platform scaffold and how placement selection works across CPU, CUDA, and Apple Metal MPS environments.

## Placement Model

Deployments can request:

- `cpu`
- `mps`
- `cuda`

The runtime resolves the requested placement against detected host capabilities and can fall back through an ordered list. The deployment record stores the resolved placement in metadata.

## Initial Real Backend

The initial executable runtime is an in-process HuggingFace Transformers backend intended for:

- local development
- smoke tests
- basic integration validation

It is not intended to replace vLLM for production throughput.

## Configuration

Set the serving runtime implementation to `huggingface-transformers` and choose a default placement:

```yaml
serving:
  implementation: huggingface-transformers
  default_engine: huggingface-transformers
  supported_engines:
    - huggingface-transformers
  default_placement: mps
  fallback_placements:
    - cpu
```

## Model Source Resolution

The runtime requires an upstream model identifier, provided through model or deployment metadata:

```yaml
metadata:
  source_model_id: Qwen/Qwen3-1.7B
```

## Smoke Test

Use the provided script:

```bash
python scripts/smoke_test_hosting.py --model-source-id Qwen/Qwen3-1.7B --placement mps
```

## Operational Notes

- `mps` is a strong local default for Apple Silicon developer hosts.
- `cpu` remains the portability fallback for CI and constrained environments.
- `cuda` is expected to become the default production placement once real GPU fleet orchestration is added.
