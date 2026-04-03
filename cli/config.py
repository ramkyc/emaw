"""TOML persistence for workspace configuration."""

import tomllib
from pathlib import Path

from cli.questionnaire import WorkspaceConfig

DEFAULT_CONFIG_PATH: Path = Path.home() / ".config" / "emacs-ai-workspace" / "workspace.toml"

# None values are stored as "" (TOML has no null type).
_TOML_TEMPLATE = """\
[workspace]
emacs_style = {emacs_style!r}
profile = {profile!r}
ai_provider = {ai_provider!r}

[environment]
os_name = {os_name!r}
python_version = {python_version!r}
emacs_path = {emacs_path!r}
emacs_version = {emacs_version!r}
"""


def save(cfg: WorkspaceConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Write workspace.toml, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _TOML_TEMPLATE.format(
        emacs_style=cfg.emacs_style,
        profile=cfg.profile,
        ai_provider=cfg.ai_provider,
        os_name=cfg.os_name,
        python_version=cfg.python_version,
        emacs_path=cfg.emacs_path or "",
        emacs_version=cfg.emacs_version or "",
    )
    path.write_text(content, encoding="utf-8")


def load(path: Path = DEFAULT_CONFIG_PATH) -> WorkspaceConfig:
    """Read workspace.toml and return a WorkspaceConfig."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    ws = data["workspace"]
    env = data["environment"]
    return WorkspaceConfig(
        emacs_style=ws["emacs_style"],
        profile=ws["profile"],
        ai_provider=ws["ai_provider"],
        os_name=env["os_name"],
        python_version=env["python_version"],
        emacs_path=env["emacs_path"] or None,
        emacs_version=env["emacs_version"] or None,
    )
