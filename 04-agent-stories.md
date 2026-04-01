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
