"""Environment detection for the emaw bootstrap CLI."""

import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class EnvInfo:
    """Snapshot of the relevant local environment."""

    os_name: str            # "macos" | "linux" | "unsupported"
    python_version: str     # e.g. "3.13.1"
    python_major: int
    python_minor: int
    emacs_path: str | None      # absolute path resolved from PATH, or None
    emacs_version: str | None   # e.g. "29.4", or None if not found/parseable


def _detect_os() -> str:
    platform = sys.platform
    if platform == "darwin":
        return "macos"
    if platform.startswith("linux"):
        return "linux"
    return "unsupported"


def _detect_python() -> tuple[str, int, int]:
    info = sys.version_info
    version_str = f"{info.major}.{info.minor}.{info.micro}"
    return version_str, info.major, info.minor


def _detect_emacs() -> tuple[str | None, str | None]:
    path = shutil.which("emacs")
    if path is None:
        return None, None
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        prefix = "GNU Emacs "
        if first_line.startswith(prefix):
            emacs_version = first_line[len(prefix):].strip()
            return path, emacs_version
        return path, None
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        return path, None


def detect() -> EnvInfo:
    """Inspect the current environment and return an EnvInfo snapshot."""
    os_name = _detect_os()
    python_version, python_major, python_minor = _detect_python()
    emacs_path, emacs_version = _detect_emacs()
    return EnvInfo(
        os_name=os_name,
        python_version=python_version,
        python_major=python_major,
        python_minor=python_minor,
        emacs_path=emacs_path,
        emacs_version=emacs_version,
    )
