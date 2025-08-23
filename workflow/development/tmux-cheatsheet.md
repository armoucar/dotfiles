# Tmux Reference Guide

## What is Tmux?

**Tmux** (Terminal Multiplexer) is a powerful terminal tool that allows you to:

- Create multiple terminal sessions within a single window
- Keep sessions running even after disconnecting
- Split your terminal into panes
- Switch between multiple projects seamlessly
- Share sessions with other users

### Why Use Tmux?

- **Persistence**: Sessions survive terminal crashes or disconnections
- **Remote work**: Perfect for SSH sessions - they stay alive even if
  connection drops
- **Portability**: Same environment on any Unix-like system
- **Scriptability**: Automate complex workspace setups
- **Session sharing**: Collaborate with others in real-time

## Key Concepts

### The Prefix Key

- Default: `Ctrl-b` (written as `C-b`)
- All tmux commands start with the prefix key
- Press prefix, release, then press the command key

### Hierarchy

```text
Server (automatically starts when you run tmux)
  └── Session (workspace for a project)
        └── Window (like browser tabs)
              └── Pane (split views within a window)
```

## Installation & Basic Usage

```bash
# Install
brew install tmux

# Create sessions
tmux new -s <name>              # New named session
tmux                            # New session (auto-named)

# List/attach sessions
tmux ls                         # List all sessions
tmux a -t <name>                # Attach to session
tmux a                          # Attach to most recent

# Kill sessions
tmux kill-session -t <name>     # Kill specific session
tmux kill-server               # Kill all sessions
```

## Configuration Examples

```bash
# Mouse support
set -g mouse on

# Vi mode
set-window-option -g mode-keys vi

# Useful settings
set -g base-index 1           # Start window numbering at 1
set -g pane-base-index 1      # Start pane numbering at 1
set -g renumber-windows on    # Renumber windows when one is closed
set -g history-limit 10000    # Increase scrollback buffer

# Status bar
set -g status-position top
```

## Session Automation

```bash
# Create detached session with commands
tmux new -s dev -d
tmux send-keys -t dev 'cd ~/project' Enter
tmux split-window -t dev
tmux send-keys -t dev:0.1 'npm run dev' Enter

# Advanced operations
tmux capture-pane -t 1                # Capture pane content
tmux save-buffer ~/output.txt         # Save to file
tmux pipe-pane -t 1 'cat >> ~/log.txt' # Log pane output
```

## Pane Resizing Commands

```bash
C-b : resize-pane -L 5         # Resize left by 5
C-b : resize-pane -R 5         # Resize right by 5
C-b : resize-pane -U 5         # Resize up by 5
C-b : resize-pane -D 5         # Resize down by 5
```

---

**Quick shortcuts reference**: See `tmux-shortcuts.md`
