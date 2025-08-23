#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Completion Notification & Auto-formatting

This hook is triggered on the "Stop" event when Claude Code finishes responding.
It performs automatic formatting on files modified during the session and plays a completion sound.

Event: Stop
Actions:
1. Auto-format markdown files modified by Claude using markdownlint --fix
2. Auto-format Python files using ruff format
3. Play audio notification (Submarine.aiff)
4. Trigger tmux bell
"""

import json
import sys
import subprocess
import os
import re
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


def get_modified_files():
    """Get list of files modified by Claude during this session from command.log."""
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        log_file = os.path.join(project_dir, ".claude", "command.log")

        if not os.path.exists(log_file):
            return []

        modified_files = []
        # Read recent entries from command.log to find file modifications
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                # Look for Edit, MultiEdit, Write tool calls with file paths
                if any(tool in line for tool in ["EDIT:", "MULTIEDIT:", "WRITE:"]):
                    # Extract file path from log entry
                    match = re.search(r"(EDIT|MULTIEDIT|WRITE):\s*(.+)$", line)
                    if match:
                        file_path = match.group(2).strip()
                        if os.path.exists(file_path):
                            modified_files.append(file_path)

        return list(set(modified_files))  # Remove duplicates
    except Exception:
        return []


def trigger_tmux_bell():
    """Trigger tmux bell indicator for current window."""
    if "TMUX" not in os.environ:
        return False

    try:
        # Get the terminal device for the current tmux pane
        tmux_pane = os.environ.get("TMUX_PANE", "unknown")
        result = subprocess.run(
            ["tmux", "display-message", "-p", "-t", tmux_pane, "#{pane_tty}"],
            capture_output=True,
            text=True,
            check=True,
        )
        pane_tty = result.stdout.strip()

        # Write bell directly to the terminal device using shell redirection
        subprocess.run(["sh", "-c", f'printf "\\007" > {pane_tty}'], check=True)
        return True
    except Exception:
        # Fallback methods if the above fails
        try:
            subprocess.run(["printf", "\007"], check=True)
            return True
        except Exception:
            try:
                sys.stdout.write("\007")
                sys.stdout.flush()
                return True
            except Exception:
                return False


try:
    input_data = json.load(sys.stdin)
    current_dir = os.getcwd()

    # Get files modified by Claude during this session
    modified_files = get_modified_files()

    # Filter for markdown and Python files
    md_files = [f for f in modified_files if f.endswith(".md")]
    py_files = [f for f in modified_files if f.endswith(".py")]

    # Auto-format markdown files
    if md_files:
        try:
            # Find markdownlint config
            config_file = find_markdownlint_config(current_dir)

            # Run markdownlint --fix on only the modified markdown files
            for md_file in md_files:
                result = subprocess.run(
                    ["markdownlint", "-c", config_file, "--fix", md_file],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(f"✓ Markdownlint fixed: {os.path.basename(md_file)}")
                else:
                    print(
                        f"✓ Markdownlint processed: {os.path.basename(md_file)} (some issues may remain)"
                    )

        except Exception as e:
            print(f"⚠️  Markdownlint autofix failed: {str(e)}")

    # Auto-format Python files with ruff
    if py_files:
        try:
            for py_file in py_files:
                result = subprocess.run(
                    ["uvx", "ruff", "format", "--force-exclude", py_file],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(f"✓ Ruff formatted: {os.path.basename(py_file)}")
                else:
                    print(f"⚠️  Ruff format failed for: {os.path.basename(py_file)}")

        except Exception as e:
            print(f"⚠️  Ruff format failed: {str(e)}")

    # Trigger tmux bell indicator
    tmux_triggered = trigger_tmux_bell()

    # Play completion sound (Submarine.aiff instead of Tink.aiff)
    completion_sound = "/System/Library/Sounds/Submarine.aiff"

    try:
        subprocess.run(["afplay", completion_sound], check=True, capture_output=True)
        tmux_status = " [tmux bell triggered]" if tmux_triggered else ""
        format_status = (
            f" [formatted {len(md_files)} md, {len(py_files)} py files]"
            if (md_files or py_files)
            else ""
        )
        print(
            f"✓ Claude Code completed - played Submarine.aiff{tmux_status}{format_status}"
        )

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback - just print completion message
        format_status = (
            f" [formatted {len(md_files)} md, {len(py_files)} py files]"
            if (md_files or py_files)
            else ""
        )
        print(f"✓ Claude Code completed{format_status}")

except Exception as e:
    print(f"Error in stop hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
