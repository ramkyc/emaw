# Architecture: Emacs AI Workspace Bootstrapper

## Architecture Summary

The product is a two-part system: an external bootstrap CLI and an internal Emacs integration layer. This separation keeps system detection, installation, and file generation outside Emacs, while keeping the final user experience inside Emacs where the workflows are executed.

## Architectural Principles

- Separate provisioning from editor runtime.
- Keep provider-specific logic isolated behind adapters.
- Generate readable configuration instead of opaque code blobs.
- Prefer profile composition over giant monolithic templates.
- Make validation a first-class subsystem.

## High-Level Components

| Component | Responsibility |
|-----------|----------------|
| Bootstrap CLI | Detect system, gather answers, install dependencies, generate config, run doctor. |
| Profile Engine | Resolve preset stack and merge package/workflow definitions. |
| Template Generator | Emit config files, docs, workflow commands, and local metadata. |
| Dependency Manager | Install/check tools like Emacs, ripgrep, Python, git, Claude Code CLI, Ollama, tree-sitter support where applicable. |
| Doctor Engine | Execute health checks and produce actionable remediation. |
| Emacs Package Layer | Provide keymaps, commands, menus, adapters, and workflow orchestration in-editor. |
| AI Provider Adapters | Interface with Claude Code, Ollama, and future backends. |

## Repository Layout

cli/
|-- profiles/      # declarative profile definitions
|-- templates/     # config + doc templates
|-- doctor/        # validation checks
`-- generator/     # file emission

## Generated Workspace Layout

~/.config/emacs-ai-workspace/
|-- workspace.toml  # product config
|-- generated/      # auto-generated files
|-- user/           # manual overrides
`-- logs/

## Language Choice: Python v1

Use Python for v1:

Why Python:

- Fast iteration for generator/orchestration workload
- Better ecosystem for YAML/TOML/JSON, templating, subprocess
- Easier cross-platform shell integration
- Lower implementation overhead

Rust later if distribution/performance becomes priority.

## AI Adapter Interface

check() -> availability
send(prompt, context) -> response
apply_patch(buffer, patch) -> result
get_health() -> status

Claude Code and Ollama adapters implement different transport methods internally.

## Persistence and State

- workspace.toml: install decisions, profiles, AI config
- manifest.json: generation metadata and version
- logs/: install/doctor history
- generated/: auto-managed files
- user/: manual overrides (never overwritten)

## Security

- No embedded secrets in generated config
- Environment variable references only
- Confirm before destructive shell commands
- Audit provider adapter boundaries

## Upgrade Model

1. Compare current manifest with generator version
2. Preview changes (diff generated files)
3. Apply updates to generated/ only
4. Rerun doctor
