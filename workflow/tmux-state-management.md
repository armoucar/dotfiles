# Tmux State Management with Claude Code Sessions

This workflow allows you to save and restore your entire tmux workspace, including resuming Claude Code conversations exactly where you left off.

## Quick Start

### Starting Claude Sessions

Always use `claude-start` instead of `claude` directly:

```bash
# In any tmux window where you want Claude
claude-start
```

This automatically generates a unique session ID and tracks it for later restoration.

### Saving Your Workspace

Before killing your tmux server or shutting down:

```bash
tmux-window-state save
```

This saves:

- All tmux sessions and windows
- Window names and working directories  
- Claude session IDs for each window that has Claude running

### Restoring Your Workspace

After restarting tmux:

```bash
tmux-window-state load
```

This recreates:

- All your previous tmux sessions
- Windows with the same names and directories
- Automatically resumes Claude conversations in the correct windows

## Typical Workflow

1. **Organize your work in tmux windows:**

   ```bash
   tmux rename-window "project_docs"
   tmux new-window -n "api_testing"  
   tmux new-window -n "debugging"
   ```

2. **Start Claude sessions where needed:**

   ```bash
   # In the "project_docs" window
   claude-start
   
   # In the "debugging" window  
   claude-start
   ```

3. **Save state when needed:**

   ```bash
   tmux-window-state save
   ```

4. **Kill tmux server or restart machine:**

   ```bash
   tmux kill-server
   ```

5. **Restore everything:**

   ```bash
   tmux new-session -d
   tmux-window-state load
   ```

## Benefits

- **Persistent conversations:** Your Claude Code sessions continue exactly where you left off
- **Window organization:** Maintain your carefully organized workspace structure  
- **Zero setup:** No manual session ID tracking or complex restoration procedures
- **Safe restarts:** Kill tmux server anytime without losing your work context

## Important Notes

- Always use `claude-start` instead of `claude` directly
- Window names are important - they're how Claude sessions are matched to windows
- You can rename and reorder windows freely; the system tracks by name, not position
- The system automatically cleans up orphaned session mappings

## Files Created

The workflow creates these tracking files (automatically managed):

- `~/.tmux-window-state` - Combined state file with sessions, windows, and Claude mappings
- `~/.tmux-claude-map` - Active Claude session tracking (updated by claude-start)
