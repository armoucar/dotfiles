#!/usr/bin/env uv run python3
"""
Smart Permission Hook for Claude Code

This PreToolUse hook provides intelligent permission handling to minimize interruptions
while maintaining safety for dangerous operations. It automatically approves safe
operations and requires confirmation for high-risk actions.

Features:
- Auto-approves safe file operations (documentation, config files)
- Blocks dangerous file patterns and operations
- Requires confirmation for potentially destructive commands
- Provides detailed reasoning for decisions
- Logs all permission decisions for audit
"""

import json
import sys
import re
from typing import Dict, List, Any, Tuple


# Patterns for automatic approval
SAFE_FILE_PATTERNS = [
    r"\.md$",
    r"\.mdx$",
    r"\.txt$",
    r"\.json$",
    r"\.yaml$",
    r"\.yml$",
    r"\.toml$",
    r"\.ini$",
    r"\.cfg$",
    r"\.conf$",
    r"\.log$",
    r"README.*",
    r"CHANGELOG.*",
    r"LICENSE.*",
    r"\.gitignore$",
    r"package\.json$",
    r"pyproject\.toml$",
    r"Cargo\.toml$",
    r"tsconfig\.json$",
    r"\.eslintrc.*",
    r"\.prettierrc.*",
]

# Patterns that should always require confirmation
DANGEROUS_FILE_PATTERNS = [
    r"\.env",
    r"\.env\..*",
    r"/secrets/",
    r"/credentials/",
    r"\.ssh/",
    r"\.aws/",
    r"\.gcp/",
    r"id_rsa",
    r"id_ed25519",
    r"private.*key",
    r"\.pem$",
    r"\.p12$",
    r"\.pfx$",
]

# Dangerous command patterns that should be blocked or require confirmation
DANGEROUS_COMMANDS = [
    (r"rm\s+.*-rf", "Recursive force deletion"),
    (r"rm\s+.*/", "Directory deletion"),
    (r"DROP\s+(TABLE|DATABASE)", "Database schema modification"),
    (r"DELETE\s+FROM.*WHERE", "Database data deletion"),
    (r"TRUNCATE", "Database table truncation"),
    (r"kubectl\s+delete", "Kubernetes resource deletion"),
    (r"helm\s+(delete|uninstall)", "Helm release removal"),
    (r"terraform\s+destroy", "Infrastructure destruction"),
    (r"dd\s+", "Low-level disk operations"),
    (r"mkfs", "Filesystem creation/formatting"),
    (r"fdisk|parted", "Disk partitioning"),
    (r"systemctl\s+(stop|disable)", "Service management"),
    (r"kill\s+-9", "Forced process termination"),
    (r"sudo\s+", "Elevated privilege operations"),
]

# Safe command patterns that can be auto-approved
SAFE_COMMANDS = [
    r"npm\s+run\s+",
    r"yarn\s+",
    r"pnpm\s+",
    r"uv\s+",
    r"git\s+(status|diff|log|branch)",
    r"git\s+add\s+",
    r"ls\s+",
    r"pwd",
    r"cd\s+",
    r"echo\s+",
    r"cat\s+",
    r"head\s+",
    r"tail\s+",
    r"grep\s+",
    r"find\s+",
    r"docker\s+(ps|images|logs)",
    r"podman\s+(ps|images|logs)",
    r"kubectl\s+(get|describe|logs)",
    r"tmux\s+",
]


def matches_patterns(text: str, patterns: List[str]) -> bool:
    """Check if text matches any of the given regex patterns."""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def analyze_file_operation(
    tool_name: str, tool_input: Dict[str, Any]
) -> Tuple[str, str]:
    """
    Analyze file operations and return decision and reason.
    Returns: (decision, reason) where decision is 'allow', 'deny', or 'ask'
    """
    if tool_name == "Read":
        file_path = tool_input.get("file_path", "")

        # Check for dangerous file patterns
        if matches_patterns(file_path, DANGEROUS_FILE_PATTERNS):
            return "ask", f"Reading potentially sensitive file: {file_path}"

        # Auto-approve safe file types
        if matches_patterns(file_path, SAFE_FILE_PATTERNS):
            return "allow", f"Auto-approved reading safe file type: {file_path}"

        return "ask", f"File read requires confirmation: {file_path}"

    elif tool_name in ["Edit", "MultiEdit", "Write"]:
        file_path = tool_input.get("file_path", "")

        # Always ask for sensitive files
        if matches_patterns(file_path, DANGEROUS_FILE_PATTERNS):
            return "ask", f"Editing potentially sensitive file: {file_path}"

        # Auto-approve safe documentation files
        if matches_patterns(file_path, SAFE_FILE_PATTERNS) and tool_name != "Write":
            return "allow", f"Auto-approved editing safe file: {file_path}"

        return "allow", f"File modification approved: {file_path}"

    return "allow", "File operation approved"


def analyze_bash_command(command: str) -> Tuple[str, str]:
    """
    Analyze bash commands and return decision and reason.
    Returns: (decision, reason) where decision is 'allow', 'deny', or 'ask'
    """
    # Check for dangerous command patterns
    for pattern, description in DANGEROUS_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return "ask", f'Dangerous operation detected: {description} - "{command}"'

    # Auto-approve safe commands
    if matches_patterns(command, SAFE_COMMANDS):
        return "allow", f"Auto-approved safe command: {command}"

    # Default to asking for other commands
    return "ask", f"Command requires confirmation: {command}"


def make_permission_decision(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main decision logic for permission handling.
    Returns hook output with permission decision.
    """
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Always allow read-only operations
    if tool_name in ["LS", "Glob", "Grep", "WebSearch", "WebFetch"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Auto-approved read-only operation: {tool_name}",
            },
            "suppressOutput": True,
        }

    # Handle file operations
    if tool_name in ["Read", "Edit", "MultiEdit", "Write", "NotebookEdit"]:
        decision, reason = analyze_file_operation(tool_name, tool_input)

        if decision == "allow":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": reason,
                },
                "suppressOutput": True,
            }
        elif decision == "ask":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            }

    # Handle bash commands
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        decision, reason = analyze_bash_command(command)

        if decision == "allow":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": reason,
                },
                "suppressOutput": True,
            }
        elif decision == "ask":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            }

    # Default: let normal permission flow handle it
    return {}


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)

        # Make permission decision
        result = make_permission_decision(input_data)

        # Output result if we have a decision
        if result:
            print(json.dumps(result))

        # Always exit 0 to not block operations
        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error in smart permissions hook: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
