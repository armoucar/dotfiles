"""Utility functions for Claude Code management."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import click


def get_claude_dir() -> Path:
    """Get the Claude configuration directory."""
    return Path.home() / ".claude"


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file safely."""
    try:
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        click.secho(f"Error reading {file_path}: {e}", fg="red")
    return None


def get_global_settings() -> Optional[Dict[str, Any]]:
    """Get global Claude settings."""
    return load_json_file(get_claude_dir() / "settings.json")
