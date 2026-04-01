"""Tests for environment detection – Story 1.2."""

import re
import subprocess
import sys

import pytest

from cli.env import EnvInfo, detect


# ---------------------------------------------------------------------------
# Real-environment tests (run on actual machine)
# ---------------------------------------------------------------------------


def test_detect_returns_envinfo():
    result = detect()
    assert isinstance(result, EnvInfo)


def test_os_name_is_known_value():
    result = detect()
    assert result.os_name in {"macos", "linux", "unsupported"}


def test_python_version_format():
    result = detect()
    assert re.fullmatch(r"\d+\.\d+\.\d+", result.python_version)


def test_python_major_minor_consistent():
    result = detect()
    assert result.python_major == sys.version_info.major
    assert result.python_minor == sys.version_info.minor


def test_emacs_path_is_none_or_nonempty_string():
    result = detect()
    assert result.emacs_path is None or (
        isinstance(result.emacs_path, str) and len(result.emacs_path) > 0
    )


# ---------------------------------------------------------------------------
# Monkeypatched OS-name tests
# ---------------------------------------------------------------------------


def test_os_name_macos_when_platform_darwin(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    result = detect()
    assert result.os_name == "macos"


def test_os_name_linux_when_platform_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    result = detect()
    assert result.os_name == "linux"


def test_os_name_unsupported_when_platform_win32(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    # shutil.which itself branches on sys.platform; patch it out so this test
    # only exercises our _detect_os() logic, not shutil's win32 internals.
    monkeypatch.setattr("shutil.which", lambda _: None)
    result = detect()
    assert result.os_name == "unsupported"


# ---------------------------------------------------------------------------
# Monkeypatched Emacs tests
# ---------------------------------------------------------------------------


def test_emacs_version_none_when_no_emacs(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    result = detect()
    assert result.emacs_path is None
    assert result.emacs_version is None


def test_emacs_version_parsed_when_emacs_present(monkeypatch):
    fake_path = "/usr/local/bin/emacs"
    monkeypatch.setattr("shutil.which", lambda _: fake_path)

    fake_completed = subprocess.CompletedProcess(
        args=[fake_path, "--version"],
        returncode=0,
        stdout="GNU Emacs 29.4\nSome extra line\n",
        stderr="",
    )
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: fake_completed)

    result = detect()
    assert result.emacs_path == fake_path
    assert result.emacs_version == "29.4"


def test_emacs_version_none_on_subprocess_error(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/emacs")

    def raise_error(*args, **kwargs):
        raise FileNotFoundError("emacs not runnable")

    monkeypatch.setattr("subprocess.run", raise_error)

    result = detect()
    assert result.emacs_path == "/usr/bin/emacs"
    assert result.emacs_version is None
