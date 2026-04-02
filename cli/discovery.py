"""Discovery module for project-specific tasks."""

import json
import re
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]


def _discover_pyproject(project_root: Path) -> dict[str, str]:
    tasks = {}
    path = project_root / "pyproject.toml"
    if not path.is_file():
        return tasks

    try:
        content = path.read_text(encoding="utf-8")
        data = tomllib.loads(content)
    except Exception:
        return tasks

    tool = data.get("tool", {})

    # Explicit EMAW tasks
    emaw = tool.get("emaw", {})
    if isinstance(emaw, dict) and "tasks" in emaw and isinstance(emaw["tasks"], dict):
        for k, v in emaw["tasks"].items():
            if isinstance(v, str):
                tasks[k] = v

    # Implicit mappings
    if "pytest" in tool:
        tasks["run-tests"] = "pytest"
    if "black" in tool:
        tasks["format-code"] = "black ."
    if "ruff" in tool:
        tasks["lint-code"] = "ruff check ."

    return tasks


def _discover_makefile(project_root: Path) -> dict[str, str]:
    tasks = {}
    path = project_root / "Makefile"
    if not path.is_file():
        return tasks

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return tasks

    # Regex to find non-phony targets that don't start with a dot
    # Target declaration: words separated by dashes/underscores followed by colon
    pattern = re.compile(r"^([a-zA-Z0-9_-]+):")
    for line in content.splitlines():
        if not line or line.startswith("#") or line.startswith("\t"):
            continue
        match = pattern.match(line)
        if match:
            target = match.group(1)
            tasks[target] = f"make {target}"

    return tasks


def _discover_package_json(project_root: Path) -> dict[str, str]:
    tasks = {}
    path = project_root / "package.json"
    if not path.is_file():
        return tasks

    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except Exception:
        return tasks

    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        for script_name in scripts.keys():
            if isinstance(script_name, str):
                tasks[script_name] = f"npm run {script_name}"

    return tasks


def discover_tasks(project_root: Path | None = None) -> dict[str, str]:
    """Scan the project for tasks and return a dictionary mapping labels to shell commands."""
    if project_root is None:
        project_root = Path.cwd()

    tasks: dict[str, str] = {}

    # Merge order sets precedence: pyproject explicit tasks overwrite makefile/npm if name collisions
    tasks.update(_discover_package_json(project_root))
    tasks.update(_discover_makefile(project_root))
    tasks.update(_discover_pyproject(project_root))

    return tasks
