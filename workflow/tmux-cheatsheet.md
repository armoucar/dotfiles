# Tmux Cheatsheet - From Basics to Advanced

## 1. Installation

### macOS (using Homebrew)
```bash
brew install tmux
```

### Verify Installation
```bash
tmux -V
```

### First Launch
```bash
tmux
```
To exit: `Ctrl-b` then `d` (detach) or type `exit`

---

## What is Tmux?

**Tmux** (Terminal Multiplexer) is a powerful terminal tool that allows you to:
- Create multiple terminal sessions within a single window
- Keep sessions running even after disconnecting
- Split your terminal into panes
- Switch between multiple projects seamlessly
- Share sessions with other users

### Why Use Tmux with iTerm2?
While iTerm2 has its own splitting and session features, tmux provides:
- **Persistence**: Sessions survive terminal crashes or disconnections
- **Remote work**: Perfect for SSH sessions - they stay alive even if connection drops
- **Portability**: Same environment on any Unix-like system
- **Scriptability**: Automate complex workspace setups
- **Session sharing**: Collaborate with others in real-time

---

## Key Concepts (Before We Dive In)

### The Prefix Key
- Default: `Ctrl-b` (written as `C-b`)
- All tmux commands start with the prefix key
- Press prefix, release, then press the command key

### Hierarchy
```
Server (automatically starts when you run tmux)
  └── Session (workspace for a project)
        └── Window (like browser tabs)
              └── Pane (split views within a window)
```

---

## 2. Session Management

```bash
# Create sessions
tmux new -s <name>              # New named session
tmux                            # New session (auto-named)

# List/attach sessions
tmux ls                         # List all sessions
tmux a -t <name>                # Attach to session
tmux a                          # Attach to most recent

# Inside tmux
C-b d                          # Detach session
C-b s                          # Choose session interactively
C-b $                          # Rename current session
C-b ( / )                      # Previous/next session

# Kill sessions
tmux kill-session -t <name>     # Kill specific session
tmux kill-server               # Kill all sessions
```

---

## 3. Window Management

```bash
# Create/navigate windows
C-b c                          # Create new window
C-b ,                          # Rename current window
C-b n / p                      # Next/previous window
C-b 0-9                        # Switch to window by number
C-b w                          # Choose window interactively
C-b &                          # Kill current window
C-b f                          # Find window by name

# Window shortcuts
C-b l                          # Last window
C-b .                          # Move window (renumber)
```

---

## 4. Pane Management

```bash
# Split panes
C-b %                          # Split horizontally (left/right)
C-b "                          # Split vertically (top/bottom)

# Navigate panes
C-b Arrow Keys                 # Move between panes
C-b o                          # Cycle through panes
C-b ;                          # Last pane
C-b q                          # Show pane numbers (then press number)

# Resize panes
C-b : resize-pane -L 5         # Resize left by 5
C-b : resize-pane -R 5         # Resize right by 5
C-b : resize-pane -U 5         # Resize up by 5
C-b : resize-pane -D 5         # Resize down by 5

# Pane operations
C-b x                          # Kill current pane
C-b z                          # Zoom/unzoom pane (fullscreen toggle)
C-b {                          # Move pane left
C-b }                          # Move pane right
C-b !                          # Convert pane to window
C-b Space                      # Cycle through pane layouts
```

---

## 5. Copy Mode & Scrolling

```bash
# Enter copy mode
C-Space [                      # Enter copy mode (like vim normal mode)
C-Space PgUp                   # Enter copy mode and page up

# Navigation in copy mode
Arrow keys                     # Move cursor
PgUp / PgDn                    # Page up/down
g / G                          # Go to top/bottom
Ctrl-u / Ctrl-d               # Half page up/down
0 / $                          # Beginning/end of line
w / b                          # Next/previous word

# Search in copy mode
/                              # Search forward
?                              # Search backward
n / N                          # Next/previous search result

# Selection and copying
Space                          # Start selection
Enter                          # Copy selection and exit copy mode
Escape                         # Exit copy mode without copying
v                              # Rectangle/block selection toggle

# Paste
C-Space ]                      # Paste last copied text
```

---

## 6. Customization & Configuration

```bash
# Mouse support
set -g mouse on                # Enable mouse (scroll, click, resize)

# Vi mode
set-window-option -g mode-keys vi    # Use vim keybindings in copy mode

# Status bar
set -g status-position top     # Move status bar to top
set -g status-bg colour235     # Dark gray background
set -g status-fg colour136     # Yellow text

# Pane borders
set -g pane-border-style fg=colour238        # Inactive pane border
set -g pane-active-border-style fg=colour208 # Active pane border (orange)

# Useful settings
set -g base-index 1           # Start window numbering at 1
set -g pane-base-index 1      # Start pane numbering at 1
set -g renumber-windows on    # Renumber windows when one is closed
set -g history-limit 10000    # Increase scrollback buffer

# Quick config reload
bind r source-file ~/.tmux.conf \; display "Config reloaded!"
```

---

## 7. Advanced Features

```bash
# Session automation
tmux new -s dev -d                    # Create detached session
tmux send-keys -t dev 'cd ~/project' Enter    # Send commands to session
tmux split-window -t dev              # Split in background
tmux send-keys -t dev:0.1 'npm run dev' Enter # Send to specific pane

# Session scripting example
tmux new -s fullstack -d
tmux send-keys -t fullstack 'cd ~/app && code .' Enter
tmux split-window -t fullstack -h
tmux send-keys -t fullstack:0.1 'npm run dev' Enter
tmux split-window -t fullstack:0.1 -v
tmux send-keys -t fullstack:0.2 'npm run test:watch' Enter

# Advanced window/pane operations
tmux swap-window -s 1 -t 2            # Swap window positions
tmux join-pane -t :1                  # Move current pane to window 1
tmux break-pane                       # Move pane to new window
tmux display-panes                    # Show pane numbers

# Capture and save
tmux capture-pane -t 1                # Capture pane content
tmux save-buffer ~/output.txt         # Save to file
tmux pipe-pane -t 1 'cat >> ~/log.txt' # Log pane output

# Useful commands
tmux clock-mode                       # Show clock
tmux choose-tree                      # Interactive session/window browser
```