#!/bin/zsh
# Claude Code Configuration Sync Script
# Syncs user-specific Claude configuration from dotfiles to ~/.claude

DOTFILES_CLAUDE="$HOME/.oh-my-zsh/custom/.claude"
GLOBAL_CLAUDE="$HOME/.claude"

# Ensure global ~/.claude directory exists
mkdir -p "$GLOBAL_CLAUDE" 2>/dev/null

# Copy all .claude contents
cp -r "$DOTFILES_CLAUDE/"* "$GLOBAL_CLAUDE/" 2>/dev/null || true

# Copy voice notifications if they exist
if [ ! -d "$DOTFILES_CLAUDE/voice_notifications" ]; then
  echo "⚠️  No voice notifications found - run 'uv run ~/.claude/generate_notification_voices.py' first" >&2
fi

# Update global settings.json with user hooks configuration

# Create the settings content
cat > "$GLOBAL_CLAUDE/settings.json" << 'EOF'
{
  "model": "opusplan",
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/notification_handler.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/command_logger.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/stop_notification_handler.py"
          }
        ]
      }
    ]
  }
}
EOF

# Script completes silently unless there are errors