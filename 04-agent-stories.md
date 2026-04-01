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
