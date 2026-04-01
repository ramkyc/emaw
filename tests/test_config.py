"""Tests for TOML config persistence – Story 1.3."""

from pathlib import Path

from cli.config import load, save
from cli.questionnaire import WorkspaceConfig

_CFG = WorkspaceConfig(
    emacs_style="minimal",
    profile="python-general",
    ai_provider="claude",
    os_name="macos",
    python_version="3.13.11",
    emacs_path="/opt/homebrew/bin/emacs",
    emacs_version="30.2",
)

_CFG_NO_EMACS = WorkspaceConfig(
    emacs_style="doom",
    profile="local-ollama",
    ai_provider="ollama",
    os_name="linux",
    python_version="3.11.0",
    emacs_path=None,
    emacs_version=None,
)


def test_save_creates_file(tmp_path: Path):
    p = tmp_path / "workspace.toml"
    save(_CFG, path=p)
    assert p.exists()


def test_save_creates_parent_dirs(tmp_path: Path):
    p = tmp_path / "a" / "b" / "workspace.toml"
    save(_CFG, path=p)
    assert p.exists()


def test_save_toml_structure(tmp_path: Path):
    p = tmp_path / "workspace.toml"
    save(_CFG, path=p)
    content = p.read_text()
    assert "[workspace]" in content
    assert "[environment]" in content


def test_load_round_trips(tmp_path: Path):
    p = tmp_path / "workspace.toml"
    save(_CFG, path=p)
    assert load(path=p) == _CFG


def test_load_none_emacs_path(tmp_path: Path):
    p = tmp_path / "workspace.toml"
    save(_CFG_NO_EMACS, path=p)
    loaded = load(path=p)
    assert loaded.emacs_path is None
    assert loaded.emacs_version is None


def test_save_overwrites_existing(tmp_path: Path):
    p = tmp_path / "workspace.toml"
    save(_CFG, path=p)
    save(_CFG_NO_EMACS, path=p)
    assert load(path=p).emacs_style == "doom"
