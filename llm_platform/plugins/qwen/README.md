# qwen plugin

## Purpose

Reference plugin package for the Qwen model family.

## Responsibilities

- Provide family metadata
- Advertise supported engines and capabilities
- Keep family-specific defaults outside the core

## Architecture

This package contains a lightweight plugin manifest and no special treatment from the core platform.

## Public APIs

- `QwenPlugin`

## Extension Points

- Family-specific compatibility rules
- Default configuration templates

## Configuration Examples

- Enable through `configs/platform.yaml`

## Failure Modes

- Misdeclared engine support

## Testing Strategy

- Plugin registration tests
