#!/bin/bash

# Tmux configuration

# Oh-My-Zsh tmux plugin configuration
export ZSH_TMUX_AUTOSTART=true
export ZSH_TMUX_AUTONAME_SESSION=true
export ZSH_TMUX_ITERM2=true
export ZSH_TMUX_UNICODE=true

if command -v tmux &> /dev/null; then
  # Tmux is available - configuration is handled by setup-tmux.zsh
  # Run 'init-tmux' to sync tmux configuration from dotfiles
  true
fi
