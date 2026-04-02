"""Tests for profile resolution logic."""

import pytest

from cli.env import EnvInfo
from cli.profile import resolve
from cli.questionnaire import WorkspaceConfig


@pytest.fixture
def mock_env() -> EnvInfo:
    """Return a mock detected environment."""
    return EnvInfo(
        os_name="macos",
        python_version="3.12.0",
        python_major=3,
        python_minor=12,
        emacs_path="/opt/homebrew/bin/emacs",
        emacs_version="29.1",
    )


def test_resolve_python_general_claude(mock_env: EnvInfo) -> None:
    """Test resolution for a standard Python dev with Claude."""
    cfg = WorkspaceConfig(
        emacs_style="doom",
        profile="python-general",
        ai_provider="claude",
        os_name=mock_env.os_name,
        python_version=mock_env.python_version,
        emacs_path=mock_env.emacs_path,
        emacs_version=mock_env.emacs_version,
    )
    reqs = resolve(cfg)

    # Base + Profile + AI Provider
    assert "git" in reqs.system_dependencies
    assert "ripgrep" in reqs.system_dependencies
    assert "python3" in reqs.system_dependencies
    assert "pip" in reqs.system_dependencies
    assert "python-lsp-server" in reqs.system_dependencies
    # Claude adds node/npm
    assert "node" in reqs.system_dependencies
    assert "npm" in reqs.system_dependencies

    assert reqs.ai_adapters == ["claude"]

    assert "use-package" in reqs.emacs_packages
    assert "python-mode" in reqs.emacs_packages
    assert "lsp-mode" in reqs.emacs_packages


def test_resolve_local_ollama(mock_env: EnvInfo) -> None:
    """Test resolution for pure local Ollama."""
    cfg = WorkspaceConfig(
        emacs_style="minimal",
        profile="local-ollama",
        ai_provider="ollama",
        os_name=mock_env.os_name,
        python_version=mock_env.python_version,
        emacs_path=mock_env.emacs_path,
        emacs_version=mock_env.emacs_version,
    )
    reqs = resolve(cfg)

    # Ollama is deduped if both profile and provider require it
    assert reqs.system_dependencies.count("ollama") == 1
    assert "git" in reqs.system_dependencies
    assert "ellama" in reqs.emacs_packages
    assert reqs.ai_adapters == ["ollama"]


def test_resolve_unknown_profile(mock_env: EnvInfo) -> None:
    """Test resolution with an unknown profile gracefully falls back."""
    cfg = WorkspaceConfig(
        emacs_style="doom",
        profile="unknown-profile",
        ai_provider="none",
        os_name=mock_env.os_name,
        python_version=mock_env.python_version,
        emacs_path=mock_env.emacs_path,
        emacs_version=mock_env.emacs_version,
    )
    reqs = resolve(cfg)

    # Base deps only
    assert reqs.system_dependencies == ["git", "ripgrep"]
    assert reqs.emacs_packages == ["use-package"]
    assert reqs.ai_adapters == []
