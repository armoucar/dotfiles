# Tmux Quick Reference

**Prefix**: `Ctrl+Space` (custom) or `Ctrl+b` (default)

## Sessions

```bash
# Command line
tmux new -s name             # Create named session
tmux ls                      # List sessions
tmux a -t name               # Attach to session
tmux kill-session -t name    # Kill session
tmux kill-server             # Kill all sessions

# Inside tmux
C-b d                        # Detach session
C-b s                        # Choose session
C-b $                        # Rename session
```

## Windows

```bash
C-b c                        # Create window
C-b ,                        # Rename window
C-b n/p                      # Next/previous window
C-b 0-9                      # Switch to window number
C-b &                        # Kill window
C-b w                        # Choose window
```

## Panes

```bash
C-b %                        # Split horizontal
C-b "                        # Split vertical
C-b Arrow                    # Navigate panes
C-b x                        # Kill pane
C-b z                        # Zoom/unzoom pane
C-b Space                    # Cycle layouts
```

## Copy Mode

```bash
C-b [                        # Enter copy mode
Space                        # Start selection
Enter                        # Copy selection
C-b ]                        # Paste
```

## Custom Bindings

```bash
C-b r                        # Reload config
C-b K                        # Kill server
C-l                          # Clear screen (global)
```

## Setup

### Install Catppuccin Theme

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
git clone https://github.com/catppuccin/tmux.git ~/.tmux/plugins/catppuccin
tmux kill-server
```

### Requirements

- **Nerd Font** in terminal (for theme icons)
- **256-color terminal** (already configured)
