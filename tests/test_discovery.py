"""Tests for task discovery module – Story 4.4."""

import json
from pathlib import Path

import pytest

from cli.discovery import discover_tasks


# ---------------------------------------------------------------------------
# pyproject.toml discovery
# ---------------------------------------------------------------------------


def test_pyproject_explicit_emaw_tasks(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.emaw.tasks]\nbuild-docs = "mkdocs build"\ndeploy = "rsync -av . host:/"',
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert tasks["build-docs"] == "mkdocs build"
    assert tasks["deploy"] == "rsync -av . host:/"


def test_pyproject_implicit_pytest(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\ntestpaths = [\"tests\"]",
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert tasks["run-tests"] == "pytest"


def test_pyproject_implicit_black(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.black]\nline-length = 88",
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert tasks["format-code"] == "black ."


def test_pyproject_implicit_ruff(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.ruff]\nline-length = 88",
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert tasks["lint-code"] == "ruff check ."


def test_pyproject_malformed_returns_empty(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("not = valid toml ][", encoding="utf-8")
    tasks = discover_tasks(tmp_path)
    # Should not raise; malformed file → empty dict
    assert isinstance(tasks, dict)


def test_pyproject_missing_returns_empty(tmp_path: Path) -> None:
    tasks = discover_tasks(tmp_path)
    assert isinstance(tasks, dict)


# ---------------------------------------------------------------------------
# Makefile discovery
# ---------------------------------------------------------------------------


def test_makefile_basic_targets(tmp_path: Path) -> None:
    (tmp_path / "Makefile").write_text(
        "build:\n\tgcc main.c\ntest:\n\tpytest\n# comment\nclean:\n\trm -rf dist\n",
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert tasks["build"] == "make build"
    assert tasks["test"] == "make test"
    assert tasks["clean"] == "make clean"


def test_makefile_phony_skipped(tmp_path: Path) -> None:
    """Targets starting with a dot like .PHONY should not be captured."""
    (tmp_path / "Makefile").write_text(
        ".PHONY: all\nall:\n\techo done\n",
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert ".PHONY" not in tasks
    assert "all" in tasks


def test_makefile_missing_returns_empty(tmp_path: Path) -> None:
    tasks = discover_tasks(tmp_path)
    assert isinstance(tasks, dict)


# ---------------------------------------------------------------------------
# package.json discovery
# ---------------------------------------------------------------------------


def test_package_json_scripts(tmp_path: Path) -> None:
    pkg = {"name": "myapp", "scripts": {"start": "node index.js", "test": "jest", "build": "tsc"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")
    tasks = discover_tasks(tmp_path)
    assert tasks["start"] == "npm run start"
    assert tasks["test"] == "npm run test"
    assert tasks["build"] == "npm run build"


def test_package_json_no_scripts_key(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "app"}', encoding="utf-8")
    tasks = discover_tasks(tmp_path)
    assert isinstance(tasks, dict)


def test_package_json_malformed(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{bad json", encoding="utf-8")
    tasks = discover_tasks(tmp_path)
    assert isinstance(tasks, dict)


# ---------------------------------------------------------------------------
# Merge precedence: pyproject wins over Makefile / package.json
# ---------------------------------------------------------------------------


def test_precedence_pyproject_wins_on_collision(tmp_path: Path) -> None:
    # Makefile defines 'test', pyproject explicit defines 'test' too.
    (tmp_path / "Makefile").write_text("test:\n\techo makefile-test\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.emaw.tasks]\ntest = "pytest -x"',
        encoding="utf-8",
    )
    tasks = discover_tasks(tmp_path)
    assert tasks["test"] == "pytest -x"


def test_no_files_returns_empty_dict(tmp_path: Path) -> None:
    tasks = discover_tasks(tmp_path)
    assert tasks == {}


# ---------------------------------------------------------------------------
# _extract_executable heuristic (via doctor.py)
# ---------------------------------------------------------------------------


def test_extract_executable_plain() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("pytest") == "pytest"


def test_extract_executable_with_args() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("pytest tests/ -v") == "pytest"


def test_extract_executable_env_var_prefix() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("PYTHONPATH=. pytest") == "pytest"


def test_extract_executable_uv_run() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("uv run pytest") == "pytest"


def test_extract_executable_npm_run() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("npm run build") == "build"


def test_extract_executable_make() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("make test") == "test"


def test_extract_executable_poetry_run() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("poetry run black .") == "black"


def test_extract_executable_empty() -> None:
    from cli.doctor import _extract_executable
    assert _extract_executable("") == ""
