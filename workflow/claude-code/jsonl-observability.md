# JSONL Observability Logging for Claude Code

This document describes the JSONL-based observability logging system implemented for Claude Code hooks.

## Overview

The command logger hook (`command_logger.py`) writes structured JSONL (JSON Lines) logs that capture comprehensive metadata about every tool use during Claude Code sessions. This provides queryable observability into what Claude does across sessions.

## Log Format

Each line in `.claude/command.log` is a complete JSON object with the following structure:

```json
{
  "timestamp": "2025-01-24T10:30:45.123456",
  "session_id": "session_abc123",
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "cwd": "/Users/U003877/project",
  "transcript_path": "/path/to/transcript.md",
  "tool_input": {...},
  "metadata": {
    "file_paths": ["/path/to/file.py"],
    "file_operation": "update",
    "content_hash": "sha256:abc123...",
    "line_count": 42,
    "character_count": 1234
  }
}
```

## Metadata Fields by Tool Type

### File Operations (Read, Write, Edit, MultiEdit)

- `file_paths`: List of affected files
- `file_operation`: Type of operation (read/create/overwrite/update/insert/delete)
- `content_hash`: SHA-256 hash of content for audit trails
- `line_count`: Number of lines in content
- `character_count`: Total characters

### Command Execution (Bash)

- `command`: The executed command
- `timeout`: Command timeout if specified
- `run_in_background`: Whether command runs in background

### Search Operations (Grep, Glob, LS)

- `pattern`: Search pattern used
- `path`: Search directory
- `glob_pattern`: For Glob operations
- `output_mode`: For Grep (content/files_with_matches/count)

### Web Operations (WebSearch, WebFetch)

- `query`: Search query (WebSearch)
- `url`: Fetched URL (WebFetch)
- `prompt`: Processing prompt (WebFetch)

### Task Management (TodoWrite, Task, ExitPlanMode)

- `todo_count`: Number of todos
- `todo_states`: Count by status (pending/in_progress/completed)
- `subagent_type`: For Task tool

## Querying Logs with jq

### Find all files modified in a session

```bash
jq -r 'select(.session_id == "session_abc123" and .metadata.file_operation != "read") | .metadata.file_paths[]' .claude/command.log | sort -u
```

### Count tool usage by type

```bash
jq -s 'group_by(.tool_name) | map({tool: .[0].tool_name, count: length})' .claude/command.log
```

### Find all commands executed

```bash
jq -r 'select(.tool_name == "Bash") | .metadata.command' .claude/command.log
```

### Get session timeline

```bash
jq -r 'select(.session_id == "session_abc123") | "\(.timestamp) - \(.tool_name): \(.metadata.file_paths // .metadata.command // .metadata.query // "N/A")"' .claude/command.log
```

### Find large file operations

```bash
jq 'select(.metadata.character_count > 10000) | {time: .timestamp, file: .metadata.file_paths, size: .metadata.character_count}' .claude/command.log
```

### Track todo progress

```bash
jq 'select(.tool_name == "TodoWrite") | {time: .timestamp, todos: .metadata.todo_states}' .claude/command.log
```

## Session Isolation

The logging system uses `session_id` to isolate operations by session. This enables:

- Tracking what files were modified in each Claude session
- Analyzing tool usage patterns per session
- Debugging specific sessions
- Creating session activity reports

## Integration with Stop Hook

The stop hook (`stop_notification_handler.py`) reads the JSONL log to:

1. Filter entries by current `session_id`
2. Extract files modified during the session
3. Auto-format only those files (markdown with markdownlint, Python with ruff)

This ensures files are only formatted if they were actually modified in the current session, preventing unwanted formatting of unrelated files.

## Log Rotation

Consider implementing log rotation to manage file size:

```bash
# Archive old logs monthly
mv .claude/command.log .claude/command.$(date +%Y%m).log
```

## Troubleshooting

### Malformed JSON Lines

If the log contains malformed lines, use jq to filter valid JSON:

```bash
# Extract only valid JSON lines
while IFS= read -r line; do
  echo "$line" | jq -c '.' 2>/dev/null && echo "$line"
done < .claude/command.log > .claude/command.clean.log
```

### Missing Metadata

Some tools may not have all metadata fields. Use jq's `//` operator for defaults:

```bash
jq '.metadata.file_paths // []' .claude/command.log
```
