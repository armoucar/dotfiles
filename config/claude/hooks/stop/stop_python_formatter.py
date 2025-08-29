#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Python Formatter

This hook auto-formats Python files modified by Claude during the current session
using ruff format.

Event: Stop
Single Responsibility: Python file formatting
"""

import json
import sys
import subprocess
import os

# Import shared utilities using environment variables
utils_path = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
sys.path.insert(0, os.path.join(utils_path, "config", "claude", "hooks"))

try:
    from utils.session_utils import get_modified_files_from_session
except ImportError:
    # Fallback: define function inline if utils not available
    def get_modified_files_from_session(session_id):
        """Fallback implementation if utils not available."""
        try:
            if not session_id:
                return []
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
            log_file = os.path.join(project_dir, ".claude", "command.log")
            if not os.path.exists(log_file):
                return []
            modified_files = []
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get("session_id") != session_id:
                            continue
                        metadata = log_entry.get("metadata", {})
                        file_paths = metadata.get("file_paths", [])
                        file_operation = metadata.get("file_operation")
                        if file_operation in [
                            "create",
                            "overwrite",
                            "update",
                            "insert",
                        ]:
                            for file_path in file_paths:
                                if file_path and os.path.exists(file_path):
                                    modified_files.append(file_path)
                    except json.JSONDecodeError:
                        continue
            return list(set(modified_files))
        except Exception:
            return []


try:
    input_data = json.load(sys.stdin)
    current_session_id = input_data.get("session_id")

    # Get files modified by Claude during this session
    modified_files = get_modified_files_from_session(current_session_id)

    # Filter for Python files only
    py_files = [f for f in modified_files if f.endswith(".py")]

    if not py_files:
        # No Python files to process
        sys.exit(0)

    # Auto-format Python files with ruff
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
        print(f"⚠️  Python formatting failed: {str(e)}")

except Exception as e:
    print(f"Error in python formatter hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
