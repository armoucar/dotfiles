#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Auto-formatting Handler

This hook auto-formats files modified by Claude during the current session:
- Markdown files: markdownlint --fix
- Python files: ruff check --fix && ruff format

Event: Stop
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


def format_markdown_files(md_files):
    """Format markdown files using markdownlint --fix."""
    if not md_files:
        return

    for md_file in md_files:
        try:
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
            print(f"⚠️  Markdownlint failed for {os.path.basename(md_file)}: {str(e)}")


def format_python_files(py_files):
    """Format Python files using ruff check --fix and ruff format."""
    if not py_files:
        return

    for py_file in py_files:
        try:
            # First, fix linting issues
            check_result = subprocess.run(
                ["uvx", "ruff", "check", "--fix", "--force-exclude", py_file],
                capture_output=True,
                text=True,
            )

            # Then, format the code
            format_result = subprocess.run(
                ["uvx", "ruff", "format", "--force-exclude", py_file],
                capture_output=True,
                text=True,
            )

            # Report results
            if check_result.returncode == 0 and format_result.returncode == 0:
                print(f"✓ Ruff fixed & formatted: {os.path.basename(py_file)}")
            elif format_result.returncode == 0:
                print(
                    f"✓ Ruff formatted: {os.path.basename(py_file)} (some lint issues may remain)"
                )
            else:
                print(f"⚠️  Ruff failed for: {os.path.basename(py_file)}")

        except Exception as e:
            print(f"⚠️  Ruff failed for {os.path.basename(py_file)}: {str(e)}")


try:
    input_data = json.load(sys.stdin)
    current_session_id = input_data.get("session_id")

    # Get files modified by Claude during this session
    modified_files = get_modified_files_from_session(current_session_id)

    if not modified_files:
        print("✓ Auto-format: No files to process")
        sys.exit(0)

    # Filter for markdown and Python files
    md_files = [f for f in modified_files if f.endswith(".md")]
    py_files = [f for f in modified_files if f.endswith(".py")]

    # Auto-format files
    format_markdown_files(md_files)
    format_python_files(py_files)

    # Summary
    total_formatted = len(md_files) + len(py_files)
    if total_formatted > 0:
        print(f"✓ Auto-format completed: {len(md_files)} md, {len(py_files)} py files")

except Exception as e:
    print(f"Error in auto-format hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
