"""Profile definitions and resolver for Emacs workspace."""

from dataclasses import dataclass, field
from cli.questionnaire import WorkspaceConfig


@dataclass
class ProfileRequirements:
    """Consolidated requirements after resolving profiles and configs."""

    system_dependencies: list[str] = field(default_factory=list)
    emacs_packages: list[str] = field(default_factory=list)
    ai_adapters: list[str] = field(default_factory=list)
    task_commands: dict[str, str] = field(default_factory=dict)


@dataclass
class ProfileDefinition:
    """A preset workflow template."""

    name: str
    system_dependencies: list[str] = field(default_factory=list)
    emacs_packages: list[str] = field(default_factory=list)
    task_commands: dict[str, str] = field(default_factory=dict)


# Base requirements applied to all generated workspaces
_BASE_SYSTEM_DEPS = ["git", "ripgrep"]
_BASE_EMACS_PACKAGES = ["use-package"]

# The static Python registry of profiles (for MVP V1)
_PROFILES: dict[str, ProfileDefinition] = {
    "python-general": ProfileDefinition(
        name="python-general",
        system_dependencies=["python3", "pip", "python-lsp-server"],
        emacs_packages=["python-mode", "lsp-mode", "corfu", "vertico"],
        task_commands={
            "run-tests": "pytest",
            "format-code": "black .",
            "lint-code": "ruff check .",
        },
    ),
    "python-quant": ProfileDefinition(
        name="python-quant",
        system_dependencies=["python3", "pip", "python-lsp-server", "jupyter"],
        emacs_packages=["python-mode", "lsp-mode", "ein", "corfu"],
        task_commands={
            "run-backtest": "python run_backtest.py",
            "open-notebook": "jupyter notebook .",
        },
    ),
    "claude-centric": ProfileDefinition(
        name="claude-centric",
        system_dependencies=["node", "npm"],  # For claude-code cli
        emacs_packages=["markdown-mode"],
        task_commands={
            "claude-chat": "claude",
            "claude-review-diff": "git diff | claude --stdin",
        },
    ),
    "local-ollama": ProfileDefinition(
        name="local-ollama",
        system_dependencies=["ollama"],
        emacs_packages=["ellama"],
        task_commands={
            "ollama-chat": "ollama run llama3",
            "ollama-explain-code": "ollama run llama3 'Explain this code'",
        },
    ),
}


def resolve(config: WorkspaceConfig) -> ProfileRequirements:
    """Resolve a workspace configuration into concrete requirements."""
    reqs = ProfileRequirements(
        system_dependencies=_BASE_SYSTEM_DEPS.copy(),
        emacs_packages=_BASE_EMACS_PACKAGES.copy(),
        ai_adapters=[],
        task_commands={},
    )

    # 1. Apply profile requirements
    profile_def = _PROFILES.get(config.profile)
    if profile_def:
        reqs.system_dependencies.extend(profile_def.system_dependencies)
        reqs.emacs_packages.extend(profile_def.emacs_packages)
        reqs.task_commands.update(profile_def.task_commands)

    # 2. Apply AI Provider requirements
    if config.ai_provider == "claude":
        reqs.ai_adapters.append("claude")
        if "node" not in reqs.system_dependencies:
            reqs.system_dependencies.extend(["node", "npm"])
        # claude-code.el requires vterm (compiled Emacs package) and
        # the claude-code MELPA package itself
        reqs.emacs_packages.extend(["vterm", "claude-code"])
    elif config.ai_provider == "ollama":
        reqs.ai_adapters.append("ollama")
        if "ollama" not in reqs.system_dependencies:
            reqs.system_dependencies.append("ollama")
        # gptel provides Ollama support via gptel-make-ollama
        reqs.emacs_packages.append("gptel")

    # Deduplicate dependencies while preserving order
    reqs.system_dependencies = list(dict.fromkeys(reqs.system_dependencies))
    reqs.emacs_packages = list(dict.fromkeys(reqs.emacs_packages))
    reqs.ai_adapters = list(dict.fromkeys(reqs.ai_adapters))
    # dictionary keys are naturally deduplicated in reqs.task_commands using update()

    return reqs
