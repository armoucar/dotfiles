#!/usr/bin/env bash

# Tmux FZF Switcher Plugin
# A self-contained tmux plugin providing fzf-powered window and session switching

# Fixed paths - this project always exists at ~/.oh-my-zsh/custom
CUSTOM_DIR="$HOME/.oh-my-zsh/custom"
PLUGIN_DIR="$CUSTOM_DIR/config/tmux/plugins/tmux-fzf-switcher"
SCRIPTS_DIR="$PLUGIN_DIR/scripts"

# Set up key bindings for the switcher using popup dialogs

# C-b w: Show all windows and sessions (windows first, then sessions)
tmux bind-key W popup -w 90% -h 90% -E "$SCRIPTS_DIR/switcher.sh all"

# C-b s: Sessions-only switcher (replaces default choose-tree -Zs)
tmux bind-key s popup -w 90% -h 90% -E "$SCRIPTS_DIR/switcher.sh sessions"

# C-b W: Windows-only switcher (optional)
tmux bind-key w popup -w 90% -h 90% -E "$SCRIPTS_DIR/switcher.sh windows"
