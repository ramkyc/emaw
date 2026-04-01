"""Tests for the workspace doctor."""

from unittest.mock import patch

from cli.doctor import run_checks, _SYSTEM_EXEC_MAP
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
        
        # We always check emacs automatically, plus 5 deps in the list
        names = {r.name for r in results}
        assert names == {"emacs", "git", "ripgrep", "python3", "node", "jinja2"}


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

    with patch("shutil.which", side_effect=mock_which_impl), \
         patch("importlib.util.find_spec", side_effect=mock_find_impl):
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
