#!/usr/bin/env python3
"""
Shared utilities for configuration file discovery.
"""

from pathlib import Path


def find_markdownlint_config(start_dir):
    """Find .markdownlint.json config file by walking up from start_dir to $HOME."""
    current_dir = Path(start_dir).resolve()
    home_dir = Path.home()

    while current_dir >= home_dir:
        config_file = current_dir / ".markdownlint.json"
        if config_file.exists():
            return str(config_file)
        current_dir = current_dir.parent

    # Should always find one in $HOME as per user instruction
    return str(home_dir / ".markdownlint.json")
