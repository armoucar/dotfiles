#!/bin/bash

# Tmux configuration

# Oh-My-Zsh tmux plugin configuration
export ZSH_TMUX_AUTOSTART=true
export ZSH_TMUX_AUTONAME_SESSION=true
export ZSH_TMUX_ITERM2=true
export ZSH_TMUX_UNICODE=true

if command -v tmux &> /dev/null; then
  # Source the tmux config file if in a tmux session
  if [ -n "$TMUX" ]; then
    command tmux source-file ~/.oh-my-zsh/custom/config/tmux.conf 2>/dev/null || true
  fi
fi
