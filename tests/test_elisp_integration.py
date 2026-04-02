"""Integration tests for Emacs Lisp components."""

import shutil
import subprocess
from pathlib import Path

import pytest

from cli.generator import generate_workspace
from cli.questionnaire import WorkspaceConfig


@pytest.fixture
def mock_config() -> WorkspaceConfig:
    return WorkspaceConfig(
        emacs_style="minimal",
        profile="python-general",
        ai_provider="claude",
        os_name="macos",
        python_version="3.12.0",
        emacs_path="emacs",
        emacs_version="29.1",
    )


def test_emaw_mode_ert(mock_config: WorkspaceConfig, tmp_path: Path) -> None:
    """Run ERT tests against the generated emaw-mode.el."""
    emacs_bin = shutil.which("emacs")
    if not emacs_bin:
        pytest.skip("Emacs not found in PATH")

    dest_dir = tmp_path / ".emaw"
    generate_workspace(mock_config, dest_dir)
    emaw_mode_el = dest_dir / "emaw-mode.el"

    test_el = Path(__file__).parent / "test_emaw_mode.el"

    # Command to run:
    # emacs -Q --batch -l <generated/emaw-mode.el> -l <tests/test_emaw_mode.el> -f ert-run-tests-batch-and-exit
    cmd = [
        emacs_bin,
        "-Q",
        "--batch",
        "-l", str(emaw_mode_el),
        "-l", str(test_el),
        "-f", "ert-run-tests-batch-and-exit"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Emacs ERT Output:\n", result.stdout)
        print("Emacs ERT Error:\n", result.stderr)
        pytest.fail(f"ERT tests failed with code {result.returncode}")
