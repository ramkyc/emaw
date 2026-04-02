"""Doctor diagnostics and validation checks for Emacs AI Workspace."""

import importlib.util
import shutil
import urllib.request
import urllib.error
from dataclasses import dataclass

from cli.profile import ProfileRequirements
from cli.questionnaire import WorkspaceConfig


@dataclass
class CheckResult:
    """Result of a single dependency check."""

    name: str
    category: str  # "system" | "python"
    status: bool
    details: str


# Maps dependency name to executable name
_SYSTEM_EXEC_MAP = {
    "ripgrep": "rg",
    "python3": "python3",
    "pip": "pip3",
    "python-lsp-server": "pylsp",
    "jupyter": "jupyter",
    "git": "git",
    "node": "node",
    "npm": "npm",
    "ollama": "ollama",
    "emacs": "emacs",
}

# Dependencies that should be checked via python module import instead
_PYTHON_LIBS = ["jinja2"]


def _check_system_tool(name: str) -> CheckResult:
    """Check for an executable in PATH."""
    exec_name = _SYSTEM_EXEC_MAP.get(name, name)
    path = shutil.which(exec_name)

    if path:
        return CheckResult(
            name=name,
            category="system",
            status=True,
            details=f"found at {path}",
        )
    return CheckResult(
        name=name,
        category="system",
        status=False,
        details=f"missing executable '{exec_name}'",
    )


def _check_python_lib(name: str) -> CheckResult:
    """Check for a python module in the environment."""
    spec = importlib.util.find_spec(name)
    if spec is not None:
        return CheckResult(
            name=name,
            category="python",
            status=True,
            details="module found",
        )
    return CheckResult(
        name=name,
        category="python",
        status=False,
        details="module not found",
    )


def _check_ai_adapter(name: str) -> CheckResult:
    """Check if an AI adapter's required backend is reachable."""
    if name == "claude":
        path = shutil.which("claude")
        if path:
            return CheckResult(
                name=name,
                category="adapter",
                status=True,
                details=f"CLI found at {path}",
            )
        return CheckResult(
            name=name,
            category="adapter",
            status=False,
            details="missing 'claude' CLI (npm install -g @anthropic-ai/claude-code)",
        )
    elif name == "ollama":
        try:
            # Short timeout since it should be local
            urllib.request.urlopen("http://localhost:11434/", timeout=2.0)
            return CheckResult(
                name=name,
                category="adapter",
                status=True,
                details="daemon responding on localhost:11434",
            )
        except (urllib.error.URLError, TimeoutError):
            return CheckResult(
                name=name,
                category="adapter",
                status=False,
                details="connection refused or timeout on localhost:11434",
            )
    
    return CheckResult(
        name=name,
        category="adapter",
        status=False,
        details="unknown adapter type",
    )


def run_checks(reqs: ProfileRequirements, config: WorkspaceConfig) -> list[CheckResult]:
    """Execute all checks against the required dependencies."""
    results = []
    
    # Always check emacs first.
    results.append(_check_system_tool("emacs"))

    # System Dependencies
    for dep in reqs.system_dependencies:
        if dep in _PYTHON_LIBS:
            results.append(_check_python_lib(dep))
        else:
            results.append(_check_system_tool(dep))

    results.append(_check_python_lib("jinja2"))
    
    # AI Adapters
    for adapter in getattr(reqs, "ai_adapters", []):
        results.append(_check_ai_adapter(adapter))
    
    return results


def print_report(results: list[CheckResult], config: WorkspaceConfig) -> None:
    """Format and print the checklist to stdout."""
    print("\nRunning Workspace Doctor Checks")
    print("-" * 31)
    print(f"Profile: {config.profile}")
    print(f"AI Provider: {config.ai_provider}")

    system_checks = [r for r in results if r.category == "system"]
    python_checks = [r for r in results if r.category == "python"]
    adapter_checks = [r for r in results if r.category == "adapter"]

    if system_checks:
        print("\nSystem Tools:")
        for res in system_checks:
            mark = "[x]" if res.status else "[!]"
            print(f" {mark} {res.name} ({res.details})")

    if python_checks:
        print("\nPython Packages:")
        for res in python_checks:
            mark = "[x]" if res.status else "[!]"
            print(f" {mark} {res.name} ({res.details})")

    if adapter_checks:
        print("\nAI Adapters:")
        for res in adapter_checks:
            mark = "[x]" if res.status else "[!]"
            print(f" {mark} {res.name} ({res.details})")

    missing_count = sum(1 for r in results if not r.status)
    print("\nSummary:")
    if missing_count == 0:
        print("All dependencies are satisfied. You are ready to go!")
    else:
        print(f"{missing_count} missing dependencies. Please install them to ensure full functionality.")
