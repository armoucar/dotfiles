#!/usr/bin/env uv run python3
"""
Smart Permission Hook for Claude Code

Minimal hook that only blocks truly dangerous operations not covered by settings.json.
Complements the built-in permission system rather than replacing it.
"""

import json
import sys
import re


# Only the most dangerous patterns that should always be blocked
CRITICAL_DANGEROUS_COMMANDS = [
    (r"^rm\s+.*-rf\s+/", "Recursive directory deletion from root"),
    (r"^sudo\s+rm\s+.*-rf", "Sudo recursive deletion"),
    (r"^DROP\s+DATABASE", "Database deletion"),
    (r"^TRUNCATE\s+TABLE", "Table truncation"),
    (r"^kubectl\s+delete\s+namespace", "Namespace deletion"),
    (
        r"^terraform\s+destroy.*--auto-approve",
        "Auto-approved infrastructure destruction",
    ),
    (r"^dd\s+.*of=/dev/", "Direct disk writing"),
    (r"^mkfs\s+/dev/", "Filesystem formatting"),
]

# Critical sensitive file patterns
CRITICAL_SENSITIVE_FILES = [
    r"\.ssh/id_rsa$",
    r"\.ssh/id_ed25519$",
    r"/etc/passwd$",
    r"/etc/shadow$",
]


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only block critical bash commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            for pattern, description in CRITICAL_DANGEROUS_COMMANDS:
                if re.search(pattern, command, re.IGNORECASE):
                    print(
                        json.dumps(
                            {
                                "hookSpecificOutput": {
                                    "hookEventName": "PreToolUse",
                                    "permissionDecision": "ask",
                                    "permissionDecisionReason": f"Critical operation blocked: {description}",
                                }
                            }
                        )
                    )
                    sys.exit(0)

        # Only block critical sensitive files
        elif tool_name in ["Read", "Edit", "Write"]:
            file_path = tool_input.get("file_path", "")
            for pattern in CRITICAL_SENSITIVE_FILES:
                if re.search(pattern, file_path):
                    print(
                        json.dumps(
                            {
                                "hookSpecificOutput": {
                                    "hookEventName": "PreToolUse",
                                    "permissionDecision": "ask",
                                    "permissionDecisionReason": f"Critical system file access: {file_path}",
                                }
                            }
                        )
                    )
                    sys.exit(0)

        # Default: let Claude's permission system handle it
        sys.exit(0)

    except Exception:
        # Never block operations due to hook errors
        sys.exit(0)


if __name__ == "__main__":
    main()
