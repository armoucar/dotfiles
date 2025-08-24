# Tmux State Management with Claude Code

Save and restore complete tmux workspaces including Claude conversations.

## Quick Commands

```bash
# Start tracked Claude sessions
claude-start                  # Instead of 'claude' directly

# Save/restore workspace
tmux-window-state save        # Before tmux server shutdown
tmux-window-state load        # After restart

# Test the system
test-tmux-state              # Run comprehensive tests
```

## Workflow

1. **Organize workspace:**

   ```bash
   tmux rename-window "docs" 
   tmux new-window -n "api"
   ```

2. **Start Claude sessions:**

   ```bash
   claude-start              # In each window that needs Claude
   ```

3. **Save before shutdown:**

   ```bash
   tmux-window-state save    # Saves sessions + Claude mappings
   tmux kill-server
   ```

4. **Restore after restart:**

   ```bash
   tmux new-session -d
   tmux-window-state load    # Recreates sessions + resumes Claude
   ```

## Key Features

- **Complete restoration** - Sessions, windows, directories, and Claude conversations
- **Name-based tracking** - Rename/reorder windows freely without breaking mappings
- **Atomic operations** - State files updated safely with rollback on errors
- **Error handling** - Graceful recovery from missing or corrupted Claude sessions

## Files

- `~/.tmux-window-state.json` - Complete workspace state
- `~/.tmux-claude-map` - Active Claude session mappings (auto-managed)
