#!/bin/bash

# Tmux FZF Switcher Plugin - Main Switcher Script
# Usage: switcher.sh <mode>
#   mode: all|sessions|windows

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

mode="${1:-all}"

case "$mode" in
    "all")
        header="Navigate: Sessions, Windows [Tab: Toggle Preview, Ctrl+U/D: Scroll Preview]"
        {
            tmux list-windows -a -F "window: #{session_name}:#{window_index} #{window_name}#{?window_bell_flag, (NEW),}#{window_flags}"
            tmux list-sessions -F "session: #{session_name} (#{session_windows} windows)"
        }
        ;;
    "sessions")
        header="Navigate: Sessions [Tab: Toggle Preview, Ctrl+U/D: Scroll Preview]"
        tmux list-sessions -F "session: #{session_name} (#{session_windows} windows)"
        ;;
    "windows")
        header="Navigate: Windows [Tab: Toggle Preview, Ctrl+U/D: Scroll Preview]"
        tmux list-windows -a -F "window: #{session_name}:#{window_index} #{window_name}#{?window_bell_flag, (NEW),}#{window_flags}"
        ;;
    *)
        echo "Invalid mode: $mode. Use: all|sessions|windows"
        exit 1
        ;;
esac | fzf --header "$header" \
      --preview "$SCRIPT_DIR/preview.sh {}" \
      --preview-window 'down:50%:wrap' \
      --bind 'tab:toggle-preview' \
      --bind 'ctrl-u:preview-page-up' \
      --bind 'ctrl-d:preview-page-down' \
      --border \
      --height 100% | {
  read selection
  if echo "$selection" | grep -q "^session:"; then
    session_name=$(echo "$selection" | cut -d' ' -f2)
    tmux switch-client -t "$session_name"
  elif echo "$selection" | grep -q "^window:"; then
    window_target=$(echo "$selection" | cut -d' ' -f2)
    session_name=$(echo "$window_target" | cut -d':' -f1)
    tmux switch-client -t "$session_name"
    tmux select-window -t "$window_target"
  fi
}