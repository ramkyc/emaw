#!/usr/bin/env bash
# emaw quickstart installer
# Usage: sh <(curl -fsSL https://raw.githubusercontent.com/yourname/emacs_tool/main/install/quickstart.sh)
#
# What this script does:
#   1. Creates a virtualenv at ~/.local/share/emaw-venv
#   2. pip-installs emacs-ai-workspace (from PyPI or local source) into that venv
#   3. Symlinks ~/.local/bin/emaw -> the venv's emaw entry-point
#
# The script is idempotent: running it again upgrades an existing install.

set -euo pipefail

VENV_DIR="${HOME}/.local/share/emaw-venv"
BIN_DIR="${HOME}/.local/bin"
EMAW_BIN="${BIN_DIR}/emaw"

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
info()  { printf '\033[1;34m[emaw]\033[0m  %s\n' "$*"; }
ok()    { printf '\033[1;32m[emaw]\033[0m  %s\n' "$*"; }
warn()  { printf '\033[1;33m[emaw]\033[0m  %s\n' "$*" >&2; }
die()   { printf '\033[1;31m[emaw]\033[0m  ERROR: %s\n' "$*" >&2; exit 1; }

# --------------------------------------------------------------------------
# Pre-flight checks
# --------------------------------------------------------------------------
info "Checking prerequisites..."

if ! command -v python3 >/dev/null 2>&1; then
    die "python3 not found. Please install Python 3.11 or later."
fi

PYTHON_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PYTHON_MAJOR="$(python3 -c 'import sys; print(sys.version_info.major)')"
PYTHON_MINOR="$(python3 -c 'import sys; print(sys.version_info.minor)')"

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    die "Python 3.11+ is required. Found Python ${PYTHON_VERSION}."
fi

ok "Python ${PYTHON_VERSION} found."

# --------------------------------------------------------------------------
# Create or upgrade the virtualenv
# --------------------------------------------------------------------------
if [ -d "${VENV_DIR}" ]; then
    info "Existing venv found at ${VENV_DIR} — upgrading..."
else
    info "Creating venv at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

# --------------------------------------------------------------------------
# Install / upgrade emacs-ai-workspace
# --------------------------------------------------------------------------
info "Installing emacs-ai-workspace..."

# If we are running from inside a cloned repo (install/ sub-dir), install
# from source; otherwise fall back to PyPI.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_ROOT="$(dirname "${SCRIPT_DIR}")"

if [ -f "${REPO_ROOT}/pyproject.toml" ]; then
    info "Local source detected — installing from ${REPO_ROOT}"
    "${VENV_DIR}/bin/pip" install --quiet --upgrade "${REPO_ROOT}"
else
    info "Installing from PyPI..."
    "${VENV_DIR}/bin/pip" install --quiet --upgrade emacs-ai-workspace
fi

# --------------------------------------------------------------------------
# Symlink into ~/.local/bin
# --------------------------------------------------------------------------
mkdir -p "${BIN_DIR}"

if [ -L "${EMAW_BIN}" ] || [ -f "${EMAW_BIN}" ]; then
    info "Updating symlink at ${EMAW_BIN}..."
    rm -f "${EMAW_BIN}"
fi

ln -s "${VENV_DIR}/bin/emaw" "${EMAW_BIN}"
ok "Symlinked: ${EMAW_BIN} -> ${VENV_DIR}/bin/emaw"

# --------------------------------------------------------------------------
# PATH reminder
# --------------------------------------------------------------------------
case ":${PATH}:" in
    *":${BIN_DIR}:"*)
        : # already on PATH
        ;;
    *)
        warn "${BIN_DIR} is not on your PATH."
        warn "Add the following line to your shell rc file (~/.bashrc / ~/.zshrc):"
        warn ""
        warn "    export PATH=\"\${HOME}/.local/bin:\${PATH}\""
        warn ""
        ;;
esac

# --------------------------------------------------------------------------
# Verify
# --------------------------------------------------------------------------
INSTALLED_VERSION="$("${VENV_DIR}/bin/emaw" --version 2>&1 || true)"
ok "Installed: ${INSTALLED_VERSION}"
ok ""
ok "Run \`emaw init\` inside any project directory to get started."
