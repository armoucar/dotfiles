#!/bin/zsh
# Claude Code Configuration Sync Script
# Syncs user-specific Claude hooks and settings from dotfiles to ~/.claude

DOTFILES_CLAUDE="$HOME/.oh-my-zsh/custom/claude"
GLOBAL_CLAUDE="$HOME/.claude"

echo "🔄 Syncing Claude Code configuration from dotfiles..."

# Ensure global ~/.claude directory exists
mkdir -p "$GLOBAL_CLAUDE/hooks"

# Copy user-specific hooks to global location
echo "📁 Copying global hooks..."
cp "$DOTFILES_CLAUDE/global/hooks/"* "$GLOBAL_CLAUDE/hooks/" 2>/dev/null || true

# Copy utilities to global location  
echo "🛠️  Copying utilities..."
cp "$DOTFILES_CLAUDE/global/utils/"* "$GLOBAL_CLAUDE/" 2>/dev/null || true

# Copy voice notifications if they exist
echo "🔊 Copying voice notifications..."
if [ -d "$DOTFILES_CLAUDE/.claude/voice_notifications" ]; then
  cp -r "$DOTFILES_CLAUDE/.claude/voice_notifications" "$GLOBAL_CLAUDE/" 2>/dev/null || true
  echo "  ✓ Voice notifications copied"
else
  echo "  ⚠️  No voice notifications found - run 'uv run claude/global/utils/generate_notification_voices.py' first"
fi

# Update global settings.json with user hooks configuration
echo "⚙️  Updating global settings.json..."

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
    ]
  }
}
EOF

echo "✅ Claude Code configuration synced successfully!"
echo ""
echo "Global hooks available:"
ls -1 "$GLOBAL_CLAUDE/hooks/" 2>/dev/null || echo "  No hooks found"
echo ""
echo "To use project-specific hooks like file_formatter.py:"
echo "  1. Copy from: $DOTFILES_CLAUDE/project-templates/"
echo "  2. To your project's .claude/hooks/ directory"
echo "  3. Add to your project's .claude/settings.json"