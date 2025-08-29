#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Markdown Formatter

This hook auto-formats markdown files modified by Claude during the current session:
- Fixes missing code block languages (using fix-markdown-code-languages script)
- Runs markdownlint --fix for other formatting issues

Event: Stop
Single Responsibility: Markdown file formatting
"""

import json
import sys
import subprocess
import os
from pathlib import Path

# Import shared utilities using environment variables
utils_path = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
sys.path.insert(0, os.path.join(utils_path, "config", "claude", "hooks"))

try:
    from utils.session_utils import get_modified_files_from_session
    from utils.config_utils import find_markdownlint_config
except ImportError:
    # Fallback: define functions inline if utils not available
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

    def find_markdownlint_config(start_dir):
        """Fallback implementation if utils not available."""
        current_dir = Path(start_dir).resolve()
        home_dir = Path.home()
        while current_dir >= home_dir:
            config_file = current_dir / ".markdownlint.json"
            if config_file.exists():
                return str(config_file)
            current_dir = current_dir.parent
        return str(home_dir / ".markdownlint.json")


def find_language_fixer_script():
    """Find the fix-markdown-code-languages script using environment variables."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    script_path = os.path.join(project_dir, "bin", "fix-markdown-code-languages")

    # Check if script exists at project path
    if os.path.exists(script_path):
        return script_path

    # Check in ~/.oh-my-zsh/custom/bin (common dotfiles location)
    custom_path = os.path.expanduser(
        "~/.oh-my-zsh/custom/bin/fix-markdown-code-languages"
    )
    if os.path.exists(custom_path):
        return custom_path

    return None


try:
    input_data = json.load(sys.stdin)
    current_dir = os.getcwd()
    current_session_id = input_data.get("session_id")

    # Get files modified by Claude during this session
    modified_files = get_modified_files_from_session(current_session_id)

    # Filter for markdown files only
    md_files = [f for f in modified_files if f.endswith(".md")]

    if not md_files:
        # No markdown files to process
        sys.exit(0)

    # Auto-format markdown files
    try:
        # First, fix missing code block languages (MD040)
        fix_script = find_language_fixer_script()

        if fix_script and os.path.exists(fix_script):
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
                    # Continue if language fixer fails for this file
                    pass

        # Find markdownlint config
        config_file = find_markdownlint_config(current_dir)

        # Run markdownlint --fix on modified markdown files
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
        print(f"⚠️  Markdown formatting failed: {str(e)}")

except Exception as e:
    print(f"Error in markdown formatter hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
