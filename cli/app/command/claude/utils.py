"""Utility functions for Claude Code management."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import click


def get_claude_dir() -> Path:
    """Get the Claude configuration directory."""
    return Path.home() / ".claude"


def get_project_claude_dir() -> Path:
    """Get the project-specific Claude directory."""
    return Path.cwd() / ".claude"


def get_templates_dir() -> Path:
    """Get the templates directory."""
    # Use environment variable if set, otherwise default to standard location
    templates_dir = os.getenv("CLAUDE_TEMPLATES_DIR")
    if templates_dir:
        return Path(templates_dir)

    # Default: look in the config directory within the oh-my-zsh custom folder
    # This assumes we're running from within the dotfiles project structure
    custom_dir = os.getenv("DOTFILES_ROOT") or Path.cwd()
    while custom_dir != custom_dir.parent:  # Walk up until we find the right structure
        candidate = custom_dir / "config" / "claude" / "templates"
        if candidate.exists():
            return candidate
        custom_dir = custom_dir.parent

    # Fallback to a standard location if nothing found
    return Path.home() / ".oh-my-zsh" / "custom" / "config" / "claude" / "templates"


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file safely."""
    try:
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        click.secho(f"Error reading {file_path}: {e}", fg="red")
    return None


def save_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save data to a JSON file safely."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except (OSError, TypeError) as e:
        click.secho(f"Error saving {file_path}: {e}", fg="red")
        return False


def get_global_settings() -> Optional[Dict[str, Any]]:
    """Get global Claude settings."""
    return load_json_file(get_claude_dir() / "settings.json")


def get_project_settings() -> Optional[Dict[str, Any]]:
    """Get project-specific Claude settings."""
    return load_json_file(get_project_claude_dir() / "settings.json")


def list_available_templates() -> list[str]:
    """List available permission templates."""
    templates_dir = get_templates_dir()
    if not templates_dir.exists():
        return []

    templates = []
    for template_file in templates_dir.glob("*.json"):
        templates.append(template_file.stem)

    return sorted(templates)


def get_template_path(template_name: str) -> Path:
    """Get the path to a specific template."""
    return get_templates_dir() / f"{template_name}.json"


def format_permission_rules(rules: list[str], max_display: int = 5) -> str:
    """Format permission rules for display."""
    if not rules:
        return "None"

    if len(rules) <= max_display:
        return "\n".join(f"  - {rule}" for rule in rules)
    else:
        displayed = rules[:max_display]
        remaining = len(rules) - max_display
        result = "\n".join(f"  - {rule}" for rule in displayed)
        result += f"\n  ... and {remaining} more"
        return result
