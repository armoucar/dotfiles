#!/usr/bin/env bash

# Tmux FZF Switcher Plugin
# A self-contained tmux plugin providing fzf-powered window and session switching

# Get the directory of this script
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PLUGIN_DIR/scripts"

# Set up key bindings for the switcher

# C-b w: Show all windows and sessions (windows first, then sessions)
tmux bind-key w new-window -n "tmux-switcher" \
  "$SCRIPTS_DIR/switcher.sh all; tmux kill-window -t tmux-switcher 2>/dev/null || true"

# C-b s: Sessions-only switcher (replaces default choose-tree -Zs)
tmux bind-key s new-window -n "tmux-session-switcher" \
  "$SCRIPTS_DIR/switcher.sh sessions; tmux kill-window -t tmux-session-switcher 2>/dev/null || true"

# C-b W: Windows-only switcher (optional)
tmux bind-key W new-window -n "tmux-window-switcher" \
  "$SCRIPTS_DIR/switcher.sh windows; tmux kill-window -t tmux-window-switcher 2>/dev/null || true"