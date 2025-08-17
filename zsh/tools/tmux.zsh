#!/bin/bash

# Tmux configuration

# Oh-My-Zsh tmux plugin configuration
export ZSH_TMUX_AUTOSTART=true
export ZSH_TMUX_AUTONAME_SESSION=true
export ZSH_TMUX_ITERM2=true
export ZSH_TMUX_UNICODE=true

if command -v tmux &> /dev/null; then
  # Change prefix from C-b to C-Space (more ergonomic)
  tmux set-option -g prefix C-Space 2>/dev/null || true
  tmux unbind C-b 2>/dev/null || true
  tmux bind C-Space send-prefix 2>/dev/null || true

  # Disable kill confirmations by rebinding keys
  tmux bind x kill-pane 2>/dev/null || true
  tmux bind '&' kill-window 2>/dev/null || true

  # Enable vi mode for copy mode (vim-like keybindings)
  tmux set-window-option -g mode-keys vi 2>/dev/null || true

  # Enable mouse support (scroll, click, resize)
  tmux set -g mouse on 2>/dev/null || true

  # Better defaults
  tmux set -g base-index 1 2>/dev/null || true
  tmux set -g pane-base-index 1 2>/dev/null || true
  tmux set -g renumber-windows on 2>/dev/null || true
  tmux set -g history-limit 10000 2>/dev/null || true

  # Quick config reload
  tmux bind r source-file ~/.tmux.conf \; display "Config reloaded!" 2>/dev/null || true
  
  # Cleaner choose-window format (remove hostname clutter)
  tmux bind w choose-window -F "#{window_index}: #{window_name}#{window_flags}" 2>/dev/null || true
  
  # Enhanced choose-tree for batch operations (alternative to choose-window)
  tmux bind W choose-tree -F "#{window_name}#{window_flags}" 2>/dev/null || true

  # Visual improvements
  tmux set -g status-position top 2>/dev/null || true


  # No automatic layout changes - let splits work naturally
fi
