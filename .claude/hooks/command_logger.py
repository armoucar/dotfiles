#!/usr/bin/env uv run python3
"""
Command logging hook for PreToolUse event.
Logs all tool calls with timestamps for debugging and compliance.
"""
import json
import sys
from datetime import datetime
import os

try:
    input_data = json.load(sys.stdin)
    
    # Get project directory for log file
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    log_file = os.path.join(project_dir, '.claude', 'command.log')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Extract tool information
    tool_name = input_data.get('tool_name', 'Unknown')
    tool_input = input_data.get('tool_input', {})
    timestamp = datetime.now().isoformat()
    
    # Format log entry based on tool type
    if tool_name == 'Bash':
        command = tool_input.get('command', 'No command')
        description = tool_input.get('description', 'No description')
        log_entry = f"[{timestamp}] BASH: {command} - {description}"
    elif tool_name in ['Edit', 'MultiEdit', 'Write']:
        file_path = tool_input.get('file_path', 'Unknown file')
        log_entry = f"[{timestamp}] {tool_name.upper()}: {file_path}"
    else:
        log_entry = f"[{timestamp}] {tool_name.upper()}: {json.dumps(tool_input)}"
    
    # Append to log file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')
    
    print(f"✓ Logged {tool_name} command to .claude/command.log")
    
except Exception as e:
    print(f"Error logging command: {e}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation