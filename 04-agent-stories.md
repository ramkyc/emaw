# Agent Stories

## Epic 1: CLI Foundation

### Story 1.1 – CLI Skeleton ✅

**As a** developer running `emaw` for the first time,
**I want** the tool to be installable and to expose the top-level commands
`init`, `doctor`, and `sync`,
**so that** further subcommand logic has a stable, testable entrypoint to
grow into.

**Acceptance criteria:**

- `pip install -e .` succeeds without manual steps.
- `emaw init`, `emaw doctor`, and `emaw sync` each exit 0 and print a
  stub message.
- `emaw` with no arguments exits non-zero and prints usage.
- `emaw --version` prints the version string and exits 0.
- All acceptance criteria are covered by automated tests.

**Files introduced:**

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Package metadata, `emaw` console-script wiring. |
| `cli/__init__.py` | Package marker. |
| `cli/main.py` | `argparse` entrypoint; `init`, `doctor`, `sync` stubs. |
| `tests/__init__.py` | Package marker. |
| `tests/test_cli.py` | Unit + subprocess tests for CLI skeleton. |

**Not included:** environment detection, profiles, generators, adapters,
doctor logic.

**Next story:** Story 1.2 – Environment Detection.

---

### Story 1.2 – Environment Detection ✅

**As a** developer running `emaw init`,
**I want** the tool to detect my OS, Python version, and Emacs
installation automatically,
**so that** subsequent steps can make informed decisions without asking
me for information the system already knows.

**Acceptance criteria:**

- `detect()` returns an `EnvInfo` dataclass with `os_name`,
  `python_version`, `python_major`, `python_minor`, `emacs_path`, and
  `emacs_version`.
- `os_name` is `"macos"` on macOS, `"linux"` on Linux, and
  `"unsupported"` otherwise.
- `emacs_path` is `None` when Emacs is not in PATH.
- `emacs_version` is `None` when Emacs is absent or its output cannot
  be parsed.
- All acceptance criteria are covered by automated tests.

**Files introduced:**

| File | Purpose |
| --- | --- |
| `cli/env.py` | `EnvInfo` dataclass and `detect()` function. Stdlib only. |
| `tests/test_env.py` | 11 tests: real-env smoke, OS branches, Emacs path/version, error path. |

**Not included:** min-version validation, wiring into `init`, profile
resolution, doctor logic.

**Next story:** Story 1.3 – Questionnaire and Config.

---

### Story 1.3 – Questionnaire and Config ✅

**As a** developer running `emaw init`,
**I want** to answer a short setup questionnaire and have my answers saved
alongside the detected system information,
**so that** a consistent workspace configuration is persisted before code
generation begins.

**Acceptance criteria:**

- `emaw init` asks 3 questions: Emacs style, profile, AI provider.
- Each question has a sensible default (Option 1) which is selected if the user enters nothing or provides invalid input.
- System detected parameters (`os_name`, `python_version`, `emacs_path`, `emacs_version`) are merged with questionnaire answers into a single `WorkspaceConfig`.
- Configuration is saved in TOML format to `~/.config/emacs-ai-workspace/workspace.toml`.
- All criteria are verified by automated tests.

**Files introduced:**

| File | Purpose |
| --- | --- |
| `cli/questionnaire.py` | Core interactive logic, injecting `_input` for unit testing. |
| `cli/config.py` | Load/Save TOML configuration without 3rd-party dependencies. |
| `tests/test_questionnaire.py` | Tests covering inputs and environment field passing. |
| `tests/test_config.py` | Tests covering serialization, deserialization, overwrites. |

**Not included:** Config generation, doctor flow, profile resolution.

**Next story:** Story 1.4 – Profile Schema and Resolver.

---

## Epic 4: Emacs Integration

### Story 4.1: Emacs Minor Mode Integration (minimal)

**Scope**
Create the core Emacs minor mode that orchestrates emaw workflows from inside Emacs.

**Requirements**
- `emaw-mode` minor mode with basic keybindings
- Call `emaw doctor` from Emacs and display results in `*emaw-doctor*` buffer
- Call `emaw init` from Emacs with current project context
- Simple status indicator in mode-line
- No complex UI yet

**Acceptance Criteria**
- `M-x emaw-doctor` runs doctor and shows results in `*emaw-doctor*` buffer
- `M-x emaw-init` runs init and shows output
- Mode-line indicator shows "emaw" when active
- Keybindings: `C-c C-e` prefix for emaw commands
- Tests for mode activation and command execution

**Constraints**
- Use existing CLI via `async-shell-command`
- No complex async handling yet
- Simple buffer output only
- No package installation or dependency management yet

---

### Story 4.2: Emacs Task Commands Integration (minimal)

**Scope**
Expose generated workspace task commands inside Emacs through `emaw-mode`, so users can run project-specific commands from the existing `C-c C-e` prefix.

**Requirements**
- Generate Emacs Lisp commands for task commands derived from the resolved profile requirements
- Add those commands to `emaw-mode`
- Run task commands through `async-shell-command`
- Use dedicated output buffers named from the task, for example `*emaw-task-sync*`
- Keep the current `C-c C-e` prefix and extend it without changing existing bindings

**Acceptance Criteria**
- Generated `emaw-mode.el` contains interactive commands for available task commands
- At least these tasks are supported when present in the resolved profile: `sync`, `doctor`, `init`
- `M-x` can invoke generated task commands directly
- Keybindings under `C-c C-e` are added for generated tasks
- Output appears in task-specific `*emaw-*` buffers
- Tests verify command generation, keymap bindings, and Elisp loadability

**Constraints**
- Use `async-shell-command`
- No transient UI, hydra, or completion framework yet
- No dynamic runtime discovery of tasks from disk; use generated config/template context only
- No advanced async callbacks or process sentinels yet
- Keep changes small and reviewable

**Suggested keybinding model**
- `C-c C-e i` → `emaw-init`
- `C-c C-e d` → `emaw-doctor`
- `C-c C-e s` → `emaw-sync`
- Additional task bindings added dynamically via `C-c C-e t <index>` mapping deterministically.


---

### Story 4.3: Real CLI Task Execution

**Scope**
Implement actual task execution behind the existing `emaw task <name>` CLI dispatch so Emacs commands invoke real workspace tasks, not just stubs.

**Requirements**
- Extend `cmd_task()` to execute tasks from `reqs.task_commands`
- Support at least shell command execution (MVP)
- Handle task failures, output parsing, and success status
- Preserve project-root execution context from Emacs dispatch
- Add CLI `--dry-run` flag for validation

**Acceptance Criteria**
- `emaw task run-tests` executes the real task command for that label
- CLI returns non-zero exit codes on task failure
- Task output streams to stdout/stderr as expected by Emacs buffers
- Tests cover happy path, failure cases, and dry-run
- Generated Emacs commands see the same task success/failure behavior as CLI

**Constraints**
- Keep Emacs layer unchanged — only extend CLI backend
- Support shell commands first (e.g. `make test`, `black .`, `ruff check .`)
- Defer makefile/python script discovery to future stories if needed
- Tasks run from project root (`.emaw` parent directory)

**Implementation Output**
- Store resolved task commands in `.emaw/tasks.json` at generation time mapping labels to shell commands strings.
- `cmd_task()` reads `.emaw/tasks.json`, executes directly via `subprocess.run(shell=True)`.

---

## Story 4.4: Task Discovery & Validation

**Scope**
Automatically discover real project tasks from common files (pyproject.toml, Makefile, package.json) and validate task configuration during `emaw doctor`.

**Requirements**
- Scan project root for task definitions in standard formats
- Auto-populate/merge `tasks.json` with discovered commands
- `emaw doctor` validates tasks.json + dependencies + task executability
- Generate task documentation shown by Emacs command help

**Acceptance Criteria**
- `emaw init` discovers tasks from pyproject.toml/Makefile/package.json
- `emaw doctor` reports task validation status (missing deps, invalid commands)
- Emacs `C-c C-e t1` shows task docstring with discovered command
- Tests cover discovery from all three formats + validation edge cases

**Constraints**
- Discovery is additive — profile tasks always available as fallback
- Validation is non-destructive (reports only)
- Keep `tasks.json` format unchanged
