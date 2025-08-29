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


def get_modified_files_from_session(session_id):
    """Get list of files modified by Claude during this session from JSONL command.log."""
    try:
        if not session_id:
            return []

        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        log_file = os.path.join(project_dir, ".claude", "command.log")

        if not os.path.exists(log_file):
            return []

        modified_files = []
        # Parse JSONL format - each line is a JSON object
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)

                    # Only process entries from current session
                    if log_entry.get("session_id") != session_id:
                        continue

                    # Extract file paths from metadata
                    metadata = log_entry.get("metadata", {})
                    file_paths = metadata.get("file_paths", [])
                    file_operation = metadata.get("file_operation")

                    # Only include file modification operations
                    if file_operation in ["create", "overwrite", "update", "insert"]:
                        for file_path in file_paths:
                            if file_path and os.path.exists(file_path):
                                modified_files.append(file_path)

                except json.JSONDecodeError:
                    # Skip malformed JSON lines (might be old format)
                    continue

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
    current_session_id = input_data.get("session_id")

    # Get files modified by Claude during this session
    modified_files = get_modified_files_from_session(current_session_id)

    # Filter for markdown and Python files
    md_files = [f for f in modified_files if f.endswith(".md")]
    py_files = [f for f in modified_files if f.endswith(".py")]

    # Auto-format markdown files
    if md_files:
        try:
            # First, fix missing code block languages (MD040)
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
            fix_script = os.path.join(project_dir, "bin", "fix-markdown-code-languages")

            if os.path.exists(fix_script):
                for md_file in md_files:
                    try:
                        result = subprocess.run(
                            [fix_script, "--language", "text", md_file],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            print(
                                f"✓ Fixed code block languages: {os.path.basename(md_file)}"
                            )
                    except Exception:
                        # Continue if language fixer fails
                        pass

            # Find markdownlint config
            config_file = find_markdownlint_config(current_dir)

            # Run markdownlint --fix on only the modified markdown files
            for md_file in md_files:
                # Handle files outside current directory by changing to the file's directory
                file_path = Path(md_file)
                file_dir = file_path.parent
                file_name = file_path.name

                # Find markdownlint config relative to the file location
                file_config = find_markdownlint_config(str(file_dir))

                result = subprocess.run(
                    ["markdownlint", "-c", file_config, "--fix", file_name],
                    cwd=str(file_dir),
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
