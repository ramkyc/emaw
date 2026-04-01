# Product Requirements Document: Emacs AI Workspace Bootstrapper

## Product Goal

Provision an Emacs-based AI coding workspace in 10-15 minutes with first useful task completed in initial session.

## MVP Scope

**Included:**

- CLI installer (`init`, `doctor`, `sync`)
- macOS/Linux environment detection  
- Profile selection: python-general, python-quant, claude-centric, local-ollama
- Dependency installation/verification (Emacs, ripgrep, Python LSP, git, terminal)
- Generated Emacs config + task commands
- Doctor validation with actionable fixes
- Claude Code + Ollama adapters

**Excluded:**

- Windows support
- Plugin marketplace
- Broad language support beyond Python focus

## Key Functional Requirements

1. `emaw init` → detect → ask questions → generate workspace → run doctor
2. Profiles compose packages + AI adapters + task commands
3. Doctor checks: system → tools → editor → AI → workflow
4. Generated commands: send-buffer, fix-error, run-task-then-ai, review-diff
5. Readable generated config with clear user/generated file separation

## Success Metrics

- 90% init completion rate
- 85% doctor pass rate  
- <15min time-to-first-AI-action
