"""emaw – Emacs AI Workspace Bootstrapper CLI entrypoint."""

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version

from cli.config import DEFAULT_CONFIG_PATH, load, save
from cli.env import detect
from cli.questionnaire import ask
from cli.generator import generate_workspace
from cli.profile import resolve
from cli.doctor import run_checks, print_report
from pathlib import Path

try:
    _VERSION = version("emacs-ai-workspace")
except PackageNotFoundError:
    _VERSION = "0.0.0.dev0"


def cmd_init(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Run the setup questionnaire and persist the workspace config."""
    env = detect()
    cfg = ask(env)
    save(cfg)
    print(f"\nWorkspace config saved to {DEFAULT_CONFIG_PATH}")
    
    dest_dir = Path.cwd() / ".emaw"
    generate_workspace(cfg, dest_dir)
    print(f"Generated workspace files in {dest_dir}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Validate system tools and Python dependencies against the profile."""
    try:
        cfg = load()
    except Exception as e:
        print("Error: Could not load workspace.toml.")
        print("Please run `emaw init` first to generate a workspace configuration.")
        return 1
        
    reqs = resolve(cfg)
    results = run_checks(reqs, cfg)
    print_report(results, cfg)
    
    missing_deps = any(not r.status for r in results)
    return 1 if missing_deps else 0


def cmd_sync(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Stub for the sync subcommand."""
    print("emaw sync: not yet implemented")
    return 0


def cmd_task(args: argparse.Namespace) -> int:
    """Stub for the task subcommand."""
    print(f"emaw task: executing {args.task_name} (not yet implemented)")
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
    
    task_parser = subparsers.add_parser("task", help="Execute a workspace task.")
    task_parser.add_argument("task_name", help="Name of the task to execute")

    return parser


_COMMANDS = {
    "init": cmd_init,
    "doctor": cmd_doctor,
    "sync": cmd_sync,
    "task": cmd_task,
}


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = _COMMANDS[args.command]
    sys.exit(handler(args))


if __name__ == "__main__":
    main()
