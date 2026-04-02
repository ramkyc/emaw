"""Tests for CLI skeleton – Story 1.1."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from cli.main import build_parser, cmd_doctor, cmd_init, cmd_sync, cmd_task


# ---------------------------------------------------------------------------
# Unit tests: direct function calls
# ---------------------------------------------------------------------------


def test_cmd_init_returns_zero(tmp_path, monkeypatch, capsys):
    from cli.env import EnvInfo
    from cli.questionnaire import WorkspaceConfig

    fake_env = EnvInfo(
        os_name="macos", python_version="3.13.0",
        python_major=3, python_minor=13,
        emacs_path=None, emacs_version=None,
    )
    fake_cfg = WorkspaceConfig(
        emacs_style="minimal", profile="python-general",
        ai_provider="claude", os_name="macos",
        python_version="3.13.0", emacs_path=None, emacs_version=None,
    )
    monkeypatch.setattr("cli.main.detect", lambda: fake_env)
    monkeypatch.setattr("cli.main.ask", lambda env: fake_cfg)
    monkeypatch.setattr("cli.main.save", lambda cfg: None)

    parser = build_parser()
    args = parser.parse_args(["init"])
    result = cmd_init(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "saved" in captured.out


def test_cmd_doctor_returns_zero(monkeypatch, capsys):
    from cli.questionnaire import WorkspaceConfig
    fake_cfg = WorkspaceConfig(
        emacs_style="minimal", profile="python-general",
        ai_provider="claude", os_name="macos",
        python_version="3.13.0", emacs_path=None, emacs_version=None,
    )
    monkeypatch.setattr("cli.main.load", lambda: fake_cfg)
    monkeypatch.setattr("cli.main.run_checks", lambda reqs, cfg: [])
    monkeypatch.setattr("cli.main.print_report", lambda res, cfg: print("doctor mock output"))

    parser = build_parser()
    args = parser.parse_args(["doctor"])
    result = cmd_doctor(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "doctor mock output" in captured.out


def test_cmd_sync_returns_zero(capsys):
    parser = build_parser()
    args = parser.parse_args(["sync"])
    result = cmd_sync(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "sync" in captured.out


def test_cmd_task_dry_run(tmp_path, monkeypatch, capsys):
    emaw_dir = tmp_path / ".emaw"
    emaw_dir.mkdir()
    (emaw_dir / "tasks.json").write_text('{"mock-task": "echo \'hello\'"}', encoding="utf-8")
    monkeypatch.setattr("cli.main.Path.cwd", lambda: tmp_path)

    parser = build_parser()
    args = parser.parse_args(["task", "mock-task", "--dry-run"])
    result = cmd_task(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "mock-task (dry-run)" in captured.out
    assert "echo 'hello'" in captured.out


def test_cmd_task_execution_success(tmp_path, monkeypatch, capsys):
    emaw_dir = tmp_path / ".emaw"
    emaw_dir.mkdir()
    (emaw_dir / "tasks.json").write_text('{"mock-task": "echo \'hello\'"}', encoding="utf-8")
    monkeypatch.setattr("cli.main.Path.cwd", lambda: tmp_path)
    
    class MockResult:
        returncode = 0
    monkeypatch.setattr("cli.main.subprocess.run", lambda cmd, **kwargs: MockResult())

    parser = build_parser()
    args = parser.parse_args(["task", "mock-task"])
    result = cmd_task(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "[SUCCESS]" in captured.out


def test_cmd_task_execution_failure(tmp_path, monkeypatch, capsys):
    emaw_dir = tmp_path / ".emaw"
    emaw_dir.mkdir()
    (emaw_dir / "tasks.json").write_text('{"mock-task": "echo \'hello\'"}', encoding="utf-8")
    monkeypatch.setattr("cli.main.Path.cwd", lambda: tmp_path)
    
    class MockResult:
        returncode = 127
    monkeypatch.setattr("cli.main.subprocess.run", lambda cmd, **kwargs: MockResult())

    parser = build_parser()
    args = parser.parse_args(["task", "mock-task"])
    result = cmd_task(args)
    assert result == 127
    captured = capsys.readouterr()
    assert "[FAILED]" in captured.out
    assert "127" in captured.out


# ---------------------------------------------------------------------------
# Unit tests: parser behaviour
# ---------------------------------------------------------------------------


def test_parser_requires_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    assert exc_info.value.code != 0


def test_parser_rejects_unknown_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["unknown"])
    assert exc_info.value.code != 0


def test_parser_version_flag():
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# Integration tests: subprocess invocation
# ---------------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "cli.main", *args],
        capture_output=True,
        text=True,
    )


def test_subprocess_init():
    # Pipe answers so the questionnaire completes without blocking.
    result = subprocess.run(
        [sys.executable, "-m", "cli.main", "init"],
        input="1\n1\n1\n",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "saved" in result.stdout


def test_subprocess_doctor():
    result = _run("doctor")
    assert result.returncode in (0, 1)
    assert "Doctor" in result.stdout or "Error:" in result.stdout


def test_subprocess_sync():
    result = _run("sync")
    assert result.returncode == 0
    assert "sync" in result.stdout


def test_subprocess_task(tmp_path: Path):
    emaw_dir = tmp_path / ".emaw"
    emaw_dir.mkdir()
    (emaw_dir / "tasks.json").write_text('{"mock-task": "echo \\"test execution\\""}', encoding="utf-8")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())

    result = subprocess.run(
        [sys.executable, "-m", "cli.main", "task", "mock-task"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 0
    assert "[SUCCESS]" in result.stdout


def test_subprocess_no_args_fails():
    result = _run()
    assert result.returncode != 0


def test_subprocess_version():
    result = subprocess.run(
        [sys.executable, "-m", "cli.main", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
