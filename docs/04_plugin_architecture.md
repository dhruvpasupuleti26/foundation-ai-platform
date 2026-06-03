# 04 Plugin Architecture

## Goal

Allow model-family integration without teaching the core platform about concrete family names.

## Contract

Each plugin implements `IPlugin` and exposes a `PluginManifest` containing:

- `plugin_id`
- `family`
- `supported_engines`
- `capabilities`
- `metadata`

## Current Bundled Plugins

- `qwen`
- `llama`
- `mistral`
- `deepseek`

## Design Constraints

- The registry stores the family value as data, not code branching.
- The router does not inspect family names.
- Plugin registration happens during application bootstrap based on YAML configuration.

## Extension Path

Future versions should support Python entry-point discovery, semantic version compatibility, and plugin-owned compatibility rules.
