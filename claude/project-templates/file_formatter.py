#!/usr/bin/env uv run python3
"""
File formatting hook for PostToolUse event.
Automatically formats Python files with ruff after editing.
"""
import json
import sys
import os
import subprocess

try:
    input_data = json.load(sys.stdin)
    
    # Only process file editing tools
    tool_name = input_data.get('tool_name', '')
    if tool_name not in ['Edit', 'MultiEdit', 'Write']:
        sys.exit(0)
    
    file_path = input_data.get('tool_input', {}).get('file_path', '')
    if not file_path or not os.path.exists(file_path):
        sys.exit(0)
    
    # Only format Python files in this project
    _, ext = os.path.splitext(file_path)
    
    if ext == '.py':
        try:
            # Format with ruff
            subprocess.run(['uv', 'run', 'ruff', 'format', file_path], 
                         check=True, capture_output=True)
            # Fix imports and other issues with ruff
            subprocess.run(['uv', 'run', 'ruff', 'check', '--fix', file_path], 
                         check=True, capture_output=True)
            print(f"✓ Formatted {file_path} with ruff")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Ruff not available or failed, skip

except Exception as e:
    print(f"Error formatting file: {e}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation