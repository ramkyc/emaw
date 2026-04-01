"""emaw – Emacs AI Workspace Bootstrapper CLI entrypoint."""

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version

try:
    _VERSION = version("emacs-ai-workspace")
except PackageNotFoundError:
    _VERSION = "0.0.0.dev0"


def cmd_init(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Stub for the init subcommand."""
    print("emaw init: not yet implemented")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Stub for the doctor subcommand."""
    print("emaw doctor: not yet implemented")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Stub for the sync subcommand."""
    print("emaw sync: not yet implemented")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="emaw",
        description="Provision a productive AI-assisted coding environment in Emacs.",
    )
    parser.add_argument(
        "--version", action="version", version=f"emaw {_VERSION}"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    subparsers.add_parser("init", help="Initialise a new Emacs AI workspace.")
    subparsers.add_parser("doctor", help="Run workspace health checks.")
    subparsers.add_parser("sync", help="Sync workspace with the latest generated config.")

    return parser


_COMMANDS = {
    "init": cmd_init,
    "doctor": cmd_doctor,
    "sync": cmd_sync,
}


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = _COMMANDS[args.command]
    sys.exit(handler(args))


if __name__ == "__main__":
    main()
