#!/usr/bin/env sh
# install/quickstart.sh — one-command installer for emaw
# Usage: sh <(curl -fsSL https://raw.githubusercontent.com/yourname/emacs_tool/main/install/quickstart.sh)
set -e

REPO_URL="https://github.com/yourname/emacs_tool.git"
VENV_DIR="${HOME}/.local/share/emaw-venv"
BIN_DIR="${HOME}/.local/bin"
CLONE_DIR="${HOME}/.local/share/emaw-src"

# ── helpers ─────────────────────────────────────────────────────────────────

die() { echo "error: $1" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "required tool not found: $1 — please install it first"; }

echo "━━━ emaw installer ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── pre-flight checks ────────────────────────────────────────────────────────
need git
need python3

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
  || die "Python 3.11+ required (found $(python3 --version 2>&1))"

# ── clone or update ──────────────────────────────────────────────────────────
if [ -d "${CLONE_DIR}/.git" ]; then
  echo "→ Updating existing source at ${CLONE_DIR}"
  git -C "${CLONE_DIR}" pull --ff-only --quiet
else
  echo "→ Cloning emaw source to ${CLONE_DIR}"
  git clone --depth 1 "${REPO_URL}" "${CLONE_DIR}" --quiet
fi

# ── create venv and install ──────────────────────────────────────────────────
echo "→ Creating virtual environment at ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"

echo "→ Installing emaw"
"${VENV_DIR}/bin/pip" install --quiet --upgrade pip
"${VENV_DIR}/bin/pip" install --quiet --editable "${CLONE_DIR}"

# ── symlink ──────────────────────────────────────────────────────────────────
mkdir -p "${BIN_DIR}"
ln -sf "${VENV_DIR}/bin/emaw" "${BIN_DIR}/emaw"

echo ""
echo "━━━ emaw installed! ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Binary : ${BIN_DIR}/emaw"
echo "  Run    : emaw --version"
echo ""
echo "  If ${BIN_DIR} is not on your PATH, add to your shell profile:"
echo "    export PATH=\"\${HOME}/.local/bin:\${PATH}\""
echo ""
echo "  Get started:"
echo "    cd ~/your-project && emaw init"
echo ""
