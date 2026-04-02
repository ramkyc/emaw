# Emacs AI Workspace Bootstrapper

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](#)

Provision a complete, AI-assisted coding environment in Emacs with a single
command. `emaw` detects your environment, asks a few questions, and generates
ready-to-use Emacs configuration, task commands, and AI integration.

---

## Prerequisites

| Requirement | Minimum |
|---|---|
| Python | 3.11 |
| Emacs | 27 |
| git | any |

Optional but recommended: `rg` (ripgrep), `claude` CLI, or a running `ollama`
daemon, depending on your chosen AI provider.

---

## Install

### One-command install (recommended)

```sh
sh <(curl -fsSL https://raw.githubusercontent.com/yourname/emacs_tool/main/install/quickstart.sh)
```

This installs `emaw` into `~/.local/bin/emaw` with no sudo required.

### From source

```sh
git clone https://github.com/yourname/emacs_tool.git
cd emacs_tool
pip install --editable ".[dev]"
```

Confirm installation:

```sh
emaw --version
# emaw 1.0.0
```

---

## Quick Start

```sh
cd ~/my-project
emaw init
```

`emaw init` will:

1. Detect your OS, Python version, and Emacs installation
2. Ask three questions (Emacs style, workflow profile, AI provider)
3. Save your choices to `~/.config/emacs-ai-workspace/workspace.toml`
4. Generate a `.emaw/` workspace directory in your project root

### Generated `.emaw/` layout

```text
.emaw/
├── early-init.el      ← performance tweaks, loaded before init.el
├── init.el            ← package configuration, hooks
├── emaw-mode.el       ← minor mode with keybindings and task commands
├── tasks.json         ← discovered and profile task map
└── claude-adapter.el  ← AI backend (if claude or ollama profile chosen)
```

### Load in Emacs

Add to your `~/.emacs.d/init.el` or `~/.config/emacs/init.el`:

```elisp
;; Load your emaw workspace (adjust path to your project root)
(load-file "~/my-project/.emaw/init.el")
```

Or use `use-package` with `dir-locals`:

```elisp
;; .dir-locals.el in project root
((nil . ((eval . (load-file ".emaw/init.el")))))
```

---

## Emacs Integration

When `emaw-mode` is active you get a `C-c C-e` prefix with the following
keybindings:

| Key | Command | Description |
|---|---|---|
| `C-c C-e d` | `emaw-doctor` | Run workspace health checks |
| `C-c C-e i` | `emaw-init` | Re-run interactive setup |
| `C-c C-e s` | `emaw-sync` | Regenerate workspace files |
| `C-c C-e t 1` | first task | Run first discovered task |
| `C-c C-e t 2` | second task | Run second discovered task |
| `C-c C-e t N` | Nth task | … and so on |

Task completion status is shown in the mode-line:

```
 emaw:run-tests [SUCCESS]    ← after a passing run
 emaw:format-code [FAILED]   ← after a failing run
```

---

## Task Discovery

`emaw init` scans your project root for tasks in three formats and merges them
into `.emaw/tasks.json`:

### pyproject.toml

**Explicit** (highest precedence):

```toml
[tool.emaw.tasks]
build-docs = "mkdocs build"
deploy     = "rsync -av dist/ host:/var/www/"
```

**Implicit** (auto-detected from tool presence):

| Section | Generated task |
|---|---|
| `[tool.pytest.*]` | `run-tests = "pytest"` |
| `[tool.black]` | `format-code = "black ."` |
| `[tool.ruff]` | `lint-code = "ruff check ."` |

### Makefile

All `make` targets are discovered automatically:

```make
test:         # → "test": "make test"
build:        # → "build": "make build"
```

### package.json

All `scripts` entries are discovered:

```json
{"scripts": {"build": "tsc"}}   // → "build": "npm run build"
```

### Merge precedence

`pyproject.toml` explicit > `pyproject.toml` implicit > `Makefile` > `package.json` > profile defaults

---

## Workflow Profiles

| Profile | Best for | Auto-tasks |
|---|---|---|
| `python-general` | General Python projects | pytest, black, ruff |
| `python-quant` | Quantitative / data science | run-backtest, open-notebook |
| `claude-centric` | Claude-heavy workflows | claude-chat, claude-review-diff |
| `local-ollama` | Air-gapped / local LLM | ollama-chat, ollama-explain-code |

---

## emaw Commands

| Command | Description |
|---|---|
| `emaw init` | Interactive setup: questionnaire → config → generate workspace |
| `emaw sync` | Regenerate `.emaw/` from saved config (no questionnaire) |
| `emaw doctor` | Validate tools, Python packages, AI adapters, and task executability |
| `emaw task <name>` | Execute a named task from `.emaw/tasks.json` |
| `emaw task <name> --dry-run` | Print task command without executing |

### emaw doctor output example

```text
Running Workspace Doctor Checks
-------------------------------
Profile: python-general
AI Provider: claude

System Tools:
 [x] emacs (found at /usr/local/bin/emacs)
 [x] python3 (found at /usr/bin/python3)
 [!] pylsp (missing executable 'pylsp')

Python Packages:
 [x] jinja2 (module found)

AI Adapters:
 [!] claude (missing 'claude' CLI)

Tasks (3 defined, 2 executable — best-effort check):
   [x] run-tests → pytest ✓
   [x] lint-code → ruff check . ✓
   [!] format-code → black . ✗ (missing black)

Summary:
3 missing dependencies. Please install them to ensure full functionality.
```

---

## emaw sync

When you update your profile or switch AI provider, run:

```sh
emaw sync
# emaw sync: regenerated workspace in /path/to/project/.emaw
```

This re-reads `~/.config/emacs-ai-workspace/workspace.toml` and regenerates
all files in `.emaw/` — including re-discovering tasks from your project files.

---

## Repository Structure

```text
.
├── README.md
├── AGENTS.md                  ← agent working rules
├── CLAUDE.md
├── pyproject.toml
├── 01-product_brief.md
├── 02-prd.md
├── 03-architecture.md
├── 04-agent-stories.md
├── install/
│   └── quickstart.sh          ← one-command installer
├── cli/
│   ├── config.py              ← TOML persistence
│   ├── discovery.py           ← task discovery (Makefile, pyproject, package.json)
│   ├── doctor.py              ← dependency validation and reporting
│   ├── env.py                 ← environment detection
│   ├── generator.py           ← workspace file generator
│   ├── main.py                ← CLI entrypoint
│   ├── profile.py             ← profile schema and resolver
│   └── questionnaire.py       ← interactive questionnaire
├── templates/
│   ├── early-init.el.j2
│   ├── init.el.j2
│   ├── emaw-mode.el.j2
│   └── ai-adapters/
│       ├── claude.el.j2
│       └── ollama.el.j2
└── tests/
    ├── test_cli.py
    ├── test_config.py
    ├── test_discovery.py
    ├── test_doctor.py
    ├── test_elisp_integration.py
    ├── test_emaw_mode.el
    ├── test_env.py
    ├── test_generator.py
    ├── test_profile.py
    └── test_questionnaire.py
```

---

## Contributing

1. Read `AGENTS.md` before making any changes
2. Run `pytest` — all tests must pass
3. Run `ruff check .` and `black --check .` — no errors permitted
4. Implement one story at a time from `04-agent-stories.md`
5. Keep changes small and focused

---

## License

MIT — see [LICENSE](LICENSE).
