# Claude Code Hooks Management Workflow

This document describes how to manage Claude Code hooks in this dotfiles setup.

## Overview

Claude Code hooks are managed through a centralized configuration system that:

- Stores hook scripts in `.claude/hooks/`
- Uses `setup-claude.zsh` to sync configuration to `~/.claude/`
- Automatically configures all hooks in the global settings.json

## Current Hook Types

### 1. Notification Hook

- **Event**: `Notification`
- **Script**: `notification_handler.py`
- **Purpose**: Plays voice notifications with session-consistent voices
- **Audio**: Uses generated voice files or falls back to system sounds

### 2. Command Logger Hook

- **Event**: `PreToolUse`
- **Script**: `command_logger.py`
- **Purpose**: Logs all tool usage for tracking and debugging

### 3. Stop Hook

- **Event**: `Stop`
- **Script**: `stop_notification_handler.py`
- **Purpose**: Plays completion sound when Claude finishes responding
- **Audio**: Uses `Glass.aiff` system sound

## Adding New Hooks

### Step 1: Create Hook Script

Create a new Python script in `.claude/hooks/`:

```bash
# Create the script
touch .claude/hooks/your_hook_name.py
chmod +x .claude/hooks/your_hook_name.py
```

### Step 2: Update setup-claude.zsh

Add your hook configuration to the `settings.json` section in `setup-claude.zsh`:

```json
"YourEventName": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "~/.claude/hooks/your_hook_name.py"
      }
    ]
  }
]
```

### Step 3: Apply Configuration

Run the setup script to sync changes:

```bash
./setup-claude.zsh
```

## Hook Script Structure

All hook scripts should follow this pattern:

```python
#!/usr/bin/env uv run python3
"""
Description of what the hook does
Event: EventName
"""
import json
import sys

try:
    input_data = json.load(sys.stdin)
    # Process the hook data
    # Perform your actions
    print("✓ Hook completed successfully")
    
except Exception as e:
    print(f"Error in hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block Claude Code operation
```

## Audio Management

### System Sounds

Available system sounds in `/System/Library/Sounds/`:

- `Glass.aiff` (used by Stop hook)
- `Tink.aiff` (used by Notification hook fallback)
- `Basso.aiff`, `Ping.aiff`, `Pop.aiff` (alternatives)

### Voice Notifications

- Generated using `generate_notification_voices.py`
- Stored in `~/.claude/voice_notifications/[voice]/` (copied from dotfiles)
- Session-consistent voice mapping via hash

## Troubleshooting

### Hook Not Firing

1. Check if script is executable: `ls -la .claude/hooks/`
2. Verify configuration in `~/.claude/settings.json`
3. Test script manually: `echo '{}' | .claude/hooks/your_script.py`

### Audio Not Playing

1. Check file permissions and paths
2. Test with `afplay /path/to/sound.aiff`
3. Verify `uv` environment for Python scripts

### Configuration Not Applied

1. Run `./setup-claude.zsh` to sync changes
2. Check if `~/.claude/settings.json` was updated
3. Restart Claude Code if needed

## Files Modified

- `.claude/hooks/stop_notification_handler.py` (new)
- `setup-claude.zsh` (updated with Stop hook config)
