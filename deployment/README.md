# deployment

## Purpose

Hold environment and deployment assets for the platform.

## Responsibilities

- Container manifests
- Helm charts or compose files later
- Environment-specific deployment guidance

## Architecture

Deployment assets stay outside application code to separate runtime packaging from operational concerns.

## Public APIs

- None yet

## Current Assets

- `deployment/Dockerfile.gateway`: gateway container image
- `docker-compose.yml`: local multi-service stack with gateway, vLLM, and TGI profiles
- `.env.example`: environment variables for the local deployment stack

## Extension Points

- Kubernetes manifests
- Dockerfiles
- Terraform modules

## Configuration Examples

- Reference `configs/platform.yaml`

## Failure Modes

- Environment drift between manifests and code

## Testing Strategy

- Lint and smoke checks for manifests as they are added
