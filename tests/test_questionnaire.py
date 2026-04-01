"""Tests for the interactive questionnaire – Story 1.3."""

from cli.env import EnvInfo
from cli.questionnaire import WorkspaceConfig, ask

_ENV = EnvInfo(
    os_name="macos",
    python_version="3.13.11",
    python_major=3,
    python_minor=13,
    emacs_path="/opt/homebrew/bin/emacs",
    emacs_version="30.2",
)

_ENV_NO_EMACS = EnvInfo(
    os_name="linux",
    python_version="3.11.0",
    python_major=3,
    python_minor=11,
    emacs_path=None,
    emacs_version=None,
)


def _make_input(answers: list[str]):
    """Return an _input callable that pops answers in order, then returns ''."""
    remaining = list(answers)

    def _inp(prompt: str) -> str:  # noqa: ARG001
        return remaining.pop(0) if remaining else ""

    return _inp


def test_ask_returns_workspace_config():
    cfg = ask(_ENV, _input=_make_input(["1", "1", "1"]))
    assert isinstance(cfg, WorkspaceConfig)


def test_ask_accepts_valid_choices():
    cfg = ask(_ENV, _input=_make_input(["2", "3", "2"]))
    assert cfg.emacs_style == "doom"
    assert cfg.profile == "claude-centric"
    assert cfg.ai_provider == "ollama"


def test_ask_default_on_empty_input():
    cfg = ask(_ENV, _input=_make_input(["", "", ""]))
    assert cfg.emacs_style == "minimal"
    assert cfg.profile == "python-general"
    assert cfg.ai_provider == "claude"


def test_ask_default_on_invalid_input():
    # All invalid → each falls back to default.
    cfg = ask(_ENV, _input=_make_input(["99", "abc", "!!"]))
    assert cfg.emacs_style == "minimal"
    assert cfg.profile == "python-general"
    assert cfg.ai_provider == "claude"


def test_ask_copies_env_fields():
    cfg = ask(_ENV, _input=_make_input(["1", "1", "1"]))
    assert cfg.os_name == _ENV.os_name
    assert cfg.python_version == _ENV.python_version
    assert cfg.emacs_path == _ENV.emacs_path
    assert cfg.emacs_version == _ENV.emacs_version


def test_ask_with_no_emacs():
    cfg = ask(_ENV_NO_EMACS, _input=_make_input(["1", "1", "1"]))
    assert cfg.emacs_path is None
    assert cfg.emacs_version is None
