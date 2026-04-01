"""Generator module for emitting the Emacs AI Workspace files."""

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cli.profile import resolve
from cli.questionnaire import WorkspaceConfig


def generate_workspace(config: WorkspaceConfig, dest_dir: Path) -> None:
    """Resolve the profile requirements and generate the workspace files."""
    reqs = resolve(config)
    
    # Locate templates relative to the cli module
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # Ensure destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Context to pass to templates
    context = {"config": config, "reqs": reqs}
    
    # Render early-init.el
    early_init_template = env.get_template("early-init.el.j2")
    early_init_content = early_init_template.render(**context)
    (dest_dir / "early-init.el").write_text(early_init_content, encoding="utf-8")
    
    # Render init.el
    init_template = env.get_template("init.el.j2")
    init_content = init_template.render(**context)
    (dest_dir / "init.el").write_text(init_content, encoding="utf-8")
