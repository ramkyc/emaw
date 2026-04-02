"""Tests for the workspace doctor."""

import urllib.error
from io import StringIO
from unittest.mock import MagicMock, patch

from cli.doctor import _SYSTEM_EXEC_MAP, CheckResult, _check_ai_adapter, print_report, run_checks
from cli.profile import ProfileRequirements
from cli.questionnaire import WorkspaceConfig


def test_doctor_all_pass() -> None:
    """Test doctor checks when all tools are found."""
    cfg = WorkspaceConfig(
        emacs_style="minimal",
        profile="python-general",
        ai_provider="claude",
        os_name="macos",
        python_version="3.12.0",
        emacs_path="/usr/local/bin/emacs",
        emacs_version="29.1",
    )
    reqs = ProfileRequirements(
        system_dependencies=["git", "ripgrep", "python3", "node", "jinja2"],
        emacs_packages=["use-package"],
        ai_adapters=["claude"],
        task_commands=[],
    )

    with patch("shutil.which") as mock_which, patch("importlib.util.find_spec") as mock_find:
        mock_which.return_value = "/mock/path"
        mock_find.return_value = True  # Mock object to signify found

        results = run_checks(reqs, cfg)

        assert all(r.status is True for r in results)

        # We always check emacs automatically, plus 5 deps in the list, plus 1 AI adapter
        names = {r.name for r in results}
        assert names == {"emacs", "git", "ripgrep", "python3", "node", "jinja2", "claude"}


def test_doctor_missing_tools() -> None:
    """Test doctor checks when tools are missing."""
    cfg = WorkspaceConfig(
        emacs_style="minimal",
        profile="python-general",
        ai_provider="claude",
        os_name="macos",
        python_version="3.12.0",
        emacs_path="/usr/local/bin/emacs",
        emacs_version="29.1",
    )
    reqs = ProfileRequirements(
        system_dependencies=["git", "node", "jinja2"],
        emacs_packages=[],
        ai_adapters=[],
        task_commands=[],
    )

    def mock_which_impl(cmd: str) -> str | None:
        if cmd == "git":
            return "/usr/bin/git"
        return None  # everything else missing

    def mock_find_impl(name: str):
        if name == "jinja2":
            return None  # missing package
        return True

    with (
        patch("shutil.which", side_effect=mock_which_impl),
        patch("importlib.util.find_spec", side_effect=mock_find_impl),
    ):
        results = run_checks(reqs, cfg)

        r_map = {r.name: r.status for r in results}
        assert r_map["emacs"] is False
        assert r_map["git"] is True
        assert r_map["node"] is False
        assert r_map["jinja2"] is False


def test_system_exec_map() -> None:
    """Ensure our known executables are mapped properly."""
    assert _SYSTEM_EXEC_MAP["ripgrep"] == "rg"
    assert _SYSTEM_EXEC_MAP["python-lsp-server"] == "pylsp"
    assert _SYSTEM_EXEC_MAP["python3"] == "python3"


def test_check_ai_adapter_claude_found() -> None:
    with patch("shutil.which", return_value="/usr/local/bin/claude"):
        res = _check_ai_adapter("claude")
        assert res.category == "adapter"
        assert res.status is True
        assert "/usr/local/bin/claude" in res.details


def test_check_ai_adapter_claude_missing() -> None:
    with patch("shutil.which", return_value=None):
        res = _check_ai_adapter("claude")
        assert res.status is False
        assert "missing 'claude' CLI" in res.details


def test_check_ai_adapter_ollama_responding() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = MagicMock()
        res = _check_ai_adapter("ollama")
        assert res.category == "adapter"
        assert res.status is True
        assert "responding on localhost:11434" in res.details


def test_check_ai_adapter_ollama_missing() -> None:
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("mock error")):
        res = _check_ai_adapter("ollama")
        assert res.category == "adapter"
        assert res.status is False
        assert "connection refused" in res.details


def test_print_report_with_adapters() -> None:
    cfg = WorkspaceConfig(
        emacs_style="minimal",
        profile="python-general",
        ai_provider="claude",
        os_name="macos",
        python_version="3.12.0",
        emacs_path="/usr/local/bin/emacs",
        emacs_version="29.1",
    )
    results = [
        CheckResult(name="emacs", category="system", status=True, details="found"),
        CheckResult(name="claude", category="adapter", status=True, details="found claude"),
    ]

    output = StringIO()
    with patch("sys.stdout", output):
        print_report(results, cfg)

    printed = output.getvalue()
    assert "AI Adapters:" in printed
    assert "[x] claude (found claude)" in printed
