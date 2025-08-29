#!/usr/bin/env python3
"""
Shared utilities for working with Claude Code session data.
"""

import json
import os


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
