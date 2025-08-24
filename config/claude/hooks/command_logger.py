#!/usr/bin/env uv run python3
"""
Claude Code Observability Logger - PreToolUse Hook

This hook logs every tool call in JSONL format for comprehensive observability.
Each line is a self-contained JSON object with rich metadata for analysis.

Event: PreToolUse
Format: JSONL (JSON Lines)
Features:
- Session isolation via session_id
- Complete tool_input preservation
- File operation tracking and hashing
- Rich metadata for querying
- Extensible structure for future analytics
"""

import json
import sys
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content for audit trails."""
    if not content:
        return ""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def extract_file_paths_from_tool(tool_name: str, tool_input: Dict[str, Any]) -> List[str]:
    """Extract all file paths from tool input based on tool type."""
    file_paths = []
    
    # File modification tools
    if tool_name in ['Write', 'Edit', 'MultiEdit']:
        if 'file_path' in tool_input:
            file_paths.append(tool_input['file_path'])
    
    # Multi-edit extracts file path
    elif tool_name == 'MultiEdit':
        if 'file_path' in tool_input:
            file_paths.append(tool_input['file_path'])
    
    # Notebook editing
    elif tool_name == 'NotebookEdit':
        if 'notebook_path' in tool_input:
            file_paths.append(tool_input['notebook_path'])
    
    # File reading
    elif tool_name == 'Read':
        if 'file_path' in tool_input:
            file_paths.append(tool_input['file_path'])
    
    # Directory operations
    elif tool_name == 'LS':
        if 'path' in tool_input:
            file_paths.append(tool_input['path'])
    
    # Pattern matching
    elif tool_name in ['Glob', 'Grep']:
        if 'path' in tool_input:
            file_paths.append(tool_input.get('path', os.getcwd()))
    
    return file_paths


def detect_file_operation(tool_name: str, tool_input: Dict[str, Any]) -> Optional[str]:
    """Detect the type of file operation being performed."""
    if tool_name == 'Write':
        file_path = tool_input.get('file_path')
        if file_path and os.path.exists(file_path):
            return 'overwrite'
        return 'create'
    
    elif tool_name in ['Edit', 'MultiEdit']:
        return 'update'
    
    elif tool_name == 'NotebookEdit':
        edit_mode = tool_input.get('edit_mode', 'replace')
        if edit_mode == 'insert':
            return 'insert'
        elif edit_mode == 'delete':
            return 'delete'
        return 'update'
    
    elif tool_name == 'Read':
        return 'read'
    
    elif tool_name in ['LS', 'Glob', 'Grep']:
        return 'query'
    
    return None


def extract_content_metadata(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Extract content-related metadata for audit and analysis."""
    metadata = {}
    
    if tool_name == 'Write':
        content = tool_input.get('content', '')
        metadata['content_size'] = len(content)
        metadata['content_hash'] = calculate_content_hash(content)
        
        file_path = tool_input.get('file_path', '')
        if file_path:
            metadata['file_extension'] = Path(file_path).suffix.lower()
    
    elif tool_name in ['Edit', 'MultiEdit']:
        old_string = tool_input.get('old_string', '')
        new_string = tool_input.get('new_string', '')
        
        metadata['old_content_size'] = len(old_string)
        metadata['new_content_size'] = len(new_string)
        metadata['old_content_hash'] = calculate_content_hash(old_string)
        metadata['new_content_hash'] = calculate_content_hash(new_string)
        metadata['content_delta'] = len(new_string) - len(old_string)
        
        # For MultiEdit, count number of edits
        if tool_name == 'MultiEdit' and 'edits' in tool_input:
            metadata['edit_count'] = len(tool_input['edits'])
        
        file_path = tool_input.get('file_path', '')
        if file_path:
            metadata['file_extension'] = Path(file_path).suffix.lower()
    
    elif tool_name == 'NotebookEdit':
        new_source = tool_input.get('new_source', '')
        metadata['content_size'] = len(new_source)
        metadata['content_hash'] = calculate_content_hash(new_source)
        metadata['cell_type'] = tool_input.get('cell_type')
        metadata['edit_mode'] = tool_input.get('edit_mode', 'replace')
    
    elif tool_name == 'Bash':
        command = tool_input.get('command', '')
        metadata['command_length'] = len(command)
        metadata['has_description'] = bool(tool_input.get('description'))
        metadata['run_in_background'] = tool_input.get('run_in_background', False)
        metadata['timeout'] = tool_input.get('timeout')
    
    elif tool_name in ['WebFetch', 'WebSearch']:
        metadata['url'] = tool_input.get('url')
        metadata['query'] = tool_input.get('query')
        if 'prompt' in tool_input:
            metadata['prompt_size'] = len(tool_input['prompt'])
    
    elif tool_name == 'Grep':
        metadata['pattern'] = tool_input.get('pattern')
        metadata['output_mode'] = tool_input.get('output_mode', 'files_with_matches')
        metadata['case_insensitive'] = tool_input.get('-i', False)
        metadata['multiline'] = tool_input.get('multiline', False)
    
    elif tool_name == 'Read':
        metadata['offset'] = tool_input.get('offset')
        metadata['limit'] = tool_input.get('limit')
    
    return metadata


def create_log_entry(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a comprehensive log entry from hook input data."""
    timestamp = datetime.now().isoformat()
    tool_name = input_data.get('tool_name', 'Unknown')
    tool_input = input_data.get('tool_input', {})
    
    # Extract file paths
    file_paths = extract_file_paths_from_tool(tool_name, tool_input)
    
    # Detect operation type
    file_operation = detect_file_operation(tool_name, tool_input)
    
    # Extract content metadata
    content_metadata = extract_content_metadata(tool_name, tool_input)
    
    # Build metadata object
    metadata = {
        'file_paths': file_paths,
        'file_operation': file_operation,
        **content_metadata
    }
    
    # Create complete log entry
    log_entry = {
        'timestamp': timestamp,
        'session_id': input_data.get('session_id', 'unknown'),
        'hook_event_name': input_data.get('hook_event_name', 'PreToolUse'),
        'tool_name': tool_name,
        'cwd': input_data.get('cwd', os.getcwd()),
        'transcript_path': input_data.get('transcript_path'),
        'tool_input': tool_input,
        'metadata': metadata
    }
    
    return log_entry


try:
    # Load input from stdin
    input_data = json.load(sys.stdin)
    
    # Create log entry with rich metadata
    log_entry = create_log_entry(input_data)
    
    # Determine log file location
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    log_file = os.path.join(project_dir, '.claude', 'command.log')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Append JSONL entry to log file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    # Success feedback
    tool_name = input_data.get('tool_name', 'Unknown')
    file_paths = log_entry['metadata'].get('file_paths', [])
    
    if file_paths:
        file_info = f" ({len(file_paths)} files)"
    else:
        file_info = ""
        
    print(f"✓ Logged {tool_name}{file_info} to .claude/command.log")

except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
    
except Exception as e:
    print(f"Error logging command: {e}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation