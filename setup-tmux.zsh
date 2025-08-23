#!/bin/zsh
# Tmux Configuration Sync Script
# Syncs tmux configuration from dotfiles to ~/.tmux.conf

DOTFILES_TMUX="$HOME/.oh-my-zsh/custom/config/tmux.conf"
GLOBAL_TMUX="$HOME/.tmux.conf"

# Copy tmux configuration
if [ -f "$DOTFILES_TMUX" ]; then
  cp "$DOTFILES_TMUX" "$GLOBAL_TMUX"
  echo "✓ Tmux configuration synced to ~/.tmux.conf"
  
  # Reload tmux config if tmux is running
  if command -v tmux &> /dev/null && tmux list-sessions &> /dev/null; then
    tmux source-file "$GLOBAL_TMUX" 2>/dev/null && echo "✓ Tmux configuration reloaded"
  fi
else
  echo "⚠️  Tmux config not found at $DOTFILES_TMUX" >&2
fi