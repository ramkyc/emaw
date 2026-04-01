# Emacs AI Workspace Bootstrapper

A Python-first developer tool that provisions a productive AI-assisted
coding environment in Emacs.

The goal of this project is to reduce the setup burden of Emacs for
modern AI coding workflows. Instead of manually assembling packages,
language tooling, AI backends, prompts, and validation commands, this
tool will generate a working, opinionated workspace with clear upgrade
and validation paths.

## Status

Planning documents are in place.
Implementation is starting.
Current phase: bootstrap CLI and repository foundation.

## What this project will do

- Detect the local development environment
- Ask a small number of setup questions
- Generate an Emacs AI workspace
- Configure AI coding integrations such as Claude Code and local Ollama
- Provide a doctor command for validation and repair guidance
- Generate task-oriented commands for real coding workflows

## Intended architecture

- Python for the bootstrap CLI, generation logic, dependency checks,
  and doctor flow
- Emacs Lisp for in-editor commands and integration
- Declarative profiles for workflow presets
- Clear separation between generated files and user-owned files

## Source of truth documents

Read these in order:

1. `01-product_brief.md`
2. `02-prd.md`
3. `03-architecture.md`
4. `04-agent-stories.md`

Operational agent instructions live in:

- `AGENTS.md`
- `CLAUDE.md`

If there is a conflict between code and these planning documents,
stop and reconcile before proceeding.

## Repository structure

```text
.
|-- README.md
|-- AGENTS.md
|-- CLAUDE.md
|-- pyproject.toml        # package metadata, emaw console-script
|-- 01-product_brief.md
|-- 02-prd.md
|-- 03-architecture.md
|-- 04-agent-stories.md
|-- cli/
|   |-- __init__.py
|   `-- main.py           # argparse entrypoint (init, doctor, sync stubs)
`-- tests/
    |-- __init__.py
    `-- test_cli.py
```
