"""Interactive questionnaire for emaw init."""

from collections.abc import Callable
from dataclasses import dataclass

from cli.env import EnvInfo


@dataclass
class WorkspaceConfig:
    """User answers combined with environment snapshot."""

    emacs_style: str        # "minimal" | "doom"
    profile: str            # "python-general" | "python-quant" |
                            #   "claude-centric" | "local-ollama"
    ai_provider: str        # "claude" | "ollama" | "none"
    os_name: str
    python_version: str
    emacs_path: str | None
    emacs_version: str | None


_EMACS_STYLES = ["minimal", "doom"]
_PROFILES = ["python-general", "python-quant", "claude-centric", "local-ollama"]
_AI_PROVIDERS = ["claude", "ollama", "none"]


def _choose(
    options: list[str],
    default_index: int,
    _input: Callable[[str], str],
) -> str:
    """Print numbered options and return the chosen value."""
    for i, opt in enumerate(options, 1):
        print(f"      {i}) {opt}")
    try:
        raw = _input(f"  Choice [{default_index + 1}]: ").strip()
    except EOFError:
        raw = ""
    if raw == "":
        return options[default_index]
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    # Invalid input → accept default silently.
    return options[default_index]


def ask(env: EnvInfo, *, _input: Callable[[str], str] = input) -> WorkspaceConfig:
    """Present the setup questionnaire and return a WorkspaceConfig."""
    emacs_info = (
        f"Emacs {env.emacs_version} at {env.emacs_path}"
        if env.emacs_path
        else "Emacs not found in PATH"
    )
    print(f"\nDetected: {env.os_name}, Python {env.python_version}, {emacs_info}\n")

    print("[1/3] Emacs base style")
    emacs_style = _choose(_EMACS_STYLES, 0, _input)

    print("\n[2/3] Workflow profile")
    profile = _choose(_PROFILES, 0, _input)

    print("\n[3/3] AI provider")
    ai_provider = _choose(_AI_PROVIDERS, 0, _input)

    return WorkspaceConfig(
        emacs_style=emacs_style,
        profile=profile,
        ai_provider=ai_provider,
        os_name=env.os_name,
        python_version=env.python_version,
        emacs_path=env.emacs_path,
        emacs_version=env.emacs_version,
    )
