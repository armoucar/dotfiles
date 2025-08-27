#!/usr/bin/env uv run python3
"""
Smart Permission Hook for Claude Code

Minimal hook that only blocks truly dangerous operations not covered by settings.json.
Complements the built-in permission system rather than replacing it.
"""

import json
import sys
import re


# Dangerous patterns that require careful review
DANGEROUS_COMMANDS = [
    # Critical destructive operations
    (r"^rm\s+.*-rf\s+/", "Recursive directory deletion from root"),
    (r"^sudo\s+rm\s+.*-rf", "Sudo recursive deletion"),
    (r"^dd\s+.*of=/dev/", "Direct disk writing"),
    (r"^mkfs\s+/dev/", "Filesystem formatting"),
    (r"^kubectl\s+delete\s+namespace", "Namespace deletion"),
    (
        r"^terraform\s+destroy.*--auto-approve",
        "Auto-approved infrastructure destruction",
    ),
    # SQL DDL operations (moved from invalid settings patterns)
    (r"DROP\s+TABLE\s+", "SQL table deletion"),
    (r"DELETE\s+FROM\s+", "SQL bulk deletion"),
    (r"TRUNCATE\s+(TABLE\s+)?", "SQL table truncation"),
    (r"ALTER\s+TABLE\s+", "SQL table alteration"),
    (r"CREATE\s+DATABASE\s+", "SQL database creation"),
    (r"DROP\s+DATABASE\s+", "SQL database deletion"),
    # Force flags in dangerous contexts (moved from invalid settings patterns)
    (r"git\s+push.*--force", "Force push to git repository"),
    (r"git\s+push.*-f\s", "Force push to git repository (short flag)"),
    (r"rm\s+.*--force", "Force file removal"),
    (r"docker\s+.*--force", "Force Docker operation"),
    (r"kubectl\s+.*--force", "Force Kubernetes operation"),
    (r"helm\s+.*--force", "Force Helm operation"),
    # Output redirection that could hide errors (moved from invalid settings patterns)
    (r">\s*/dev/null\s*$", "Output redirection to /dev/null"),
    (r"2>\s*/dev/null\s*$", "Error redirection to /dev/null"),
    (r"&>\s*/dev/null\s*$", "All output redirection to /dev/null"),
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

        # Check for dangerous bash commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            for pattern, description in DANGEROUS_COMMANDS:
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
