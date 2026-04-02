"""Generator module for emitting the Emacs AI Workspace files."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cli.profile import resolve
from cli.questionnaire import WorkspaceConfig

# Approved adapter names.  Only these may produce generated adapter files.
_APPROVED_ADAPTERS = {"claude", "ollama"}


def generate_workspace(config: WorkspaceConfig, dest_dir: Path) -> None:
    """Resolve the profile requirements and generate the workspace files."""
    reqs = resolve(config)

    # Locate templates relative to this file's parent
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)))

    # Ensure destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Context shared by all templates
    context = {"config": config, "reqs": reqs}

    # Render early-init.el
    early_init_content = env.get_template("early-init.el.j2").render(**context)
    (dest_dir / "early-init.el").write_text(early_init_content, encoding="utf-8")

    # Render init.el
    init_content = env.get_template("init.el.j2").render(**context)
    (dest_dir / "init.el").write_text(init_content, encoding="utf-8")

    # Render one adapter file per approved AI adapter
    for adapter in reqs.ai_adapters:
        if adapter not in _APPROVED_ADAPTERS:
            continue
        adapter_template = env.get_template(f"ai-adapters/{adapter}.el.j2")
        adapter_content = adapter_template.render(**context)
        (dest_dir / f"{adapter}-adapter.el").write_text(
            adapter_content, encoding="utf-8"
        )
