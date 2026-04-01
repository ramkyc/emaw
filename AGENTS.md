# AGENTS.md

## Purpose

This repository builds an Emacs AI workspace bootstrapper: a tool that
provisions a productive AI-assisted coding environment in Emacs.

## Source of truth

Use these files as the primary planning documents, in this order:

1. `01-product_brief.md`
2. `02-prd.md`
3. `03-architecture.md`
4. `04-agent-stories.md`

If code or docs conflict with these files, stop and ask before making
assumptions.

## Working rules

- Start by reading the relevant planning docs before changing code.
- Implement one story at a time from `04-agent-stories.md`.
- Keep changes small, local, and reviewable.
- Prefer incremental commits over large rewrites.
- Do not invent new product scope unless explicitly requested.
- Do not silently replace the Python-first architecture with another stack.
- Do not add heavy dependencies without a clear reason.
- Do not overwrite user-authored files when generated and user files are
  meant to stay separate.

## Architecture constraints

- The product has two major layers: external bootstrap CLI and internal
  Emacs integration layer.
- V1 is Python-first for the CLI and generator.
- Emacs Lisp is used for in-editor commands and integration.
- Generated files and user files must remain clearly separated.
- Provider integrations must use adapter boundaries.

## Implementation priorities

Focus on this sequence unless told otherwise:

1. CLI skeleton
2. Environment detection
3. Questionnaire and config
4. Profile schema and resolver
5. Generator
6. Dependency checks
7. Emacs integration layer
8. Claude adapter
9. Doctor flow
10. Ollama adapter

## Coding guidance

- Prefer simple, explicit code over clever abstractions.
- Keep modules small and named by responsibility.
- Add docstrings or comments only where they improve maintainability.
- Avoid premature generalization.
- Keep side effects isolated.
- Prefer deterministic outputs for generators.

## File and directory guidance

Expected implementation areas:

- `cli/` for command-line entrypoints and orchestration
- `profiles/` or `cli/profiles/` for declarative profile definitions
- `templates/` for generated config and doc templates
- `doctor/` for health checks
- `emacs/` or equivalent for Emacs Lisp integration

If the actual repository structure changes, follow the codebase, then
update this file.

## Validation before completion

Before marking work complete:

- Run formatting.
- Run linting.
- Run tests for touched modules.
- Update docs if behavior or structure changed.
- Summarize assumptions and follow-up items.

## Change boundaries

Ask before:

- Changing top-level architecture
- Renaming core documents
- Switching config format
- Replacing Python with Rust
- Introducing background services or telemetry
- Expanding MVP scope

## Preferred delivery style

When completing a task:

1. State what was changed.
2. State what was not changed.
3. State validation performed.
4. State open questions or risks.
