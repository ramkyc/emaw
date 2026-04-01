"""Tests for CLI skeleton – Story 1.1."""

import subprocess
import sys

import pytest

from cli.main import build_parser, cmd_doctor, cmd_init, cmd_sync


# ---------------------------------------------------------------------------
# Unit tests: direct function calls
# ---------------------------------------------------------------------------


def test_cmd_init_returns_zero(capsys):
    parser = build_parser()
    args = parser.parse_args(["init"])
    result = cmd_init(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "init" in captured.out


def test_cmd_doctor_returns_zero(capsys):
    parser = build_parser()
    args = parser.parse_args(["doctor"])
    result = cmd_doctor(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "doctor" in captured.out


def test_cmd_sync_returns_zero(capsys):
    parser = build_parser()
    args = parser.parse_args(["sync"])
    result = cmd_sync(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "sync" in captured.out


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
    result = _run("init")
    assert result.returncode == 0
    assert "init" in result.stdout


def test_subprocess_doctor():
    result = _run("doctor")
    assert result.returncode == 0
    assert "doctor" in result.stdout


def test_subprocess_sync():
    result = _run("sync")
    assert result.returncode == 0
    assert "sync" in result.stdout


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
