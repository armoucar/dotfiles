#!/bin/bash

# Tmux FZF Switcher Plugin - Preview Script
# Usage: preview.sh "session:window" or "session: (description)"

selection="$1"

if [[ -z "$selection" ]]; then
    echo "No selection provided"
    exit 1
fi

# Extract type, session name, and window info
if echo "$selection" | grep -q "^session:"; then
    # Session preview - show active window content
    session_name=$(echo "$selection" | sed 's/^session: \([^ ]*\).*/\1/')
    
    # Get the active window in this session
    active_window=$(tmux list-windows -t "$session_name" -F "#{window_index}" -f "#{window_active}" 2>/dev/null | head -1)
    
    if [[ -n "$active_window" ]]; then
        target="${session_name}:${active_window}"
        echo "=== SESSION: $session_name (Active Window: $active_window) ==="
        echo ""
        tmux capture-pane -t "$target" -p 2>/dev/null | tail -30
    else
        echo "=== SESSION: $session_name ==="
        echo ""
        echo "No active window found or session not available"
    fi
    
elif echo "$selection" | grep -q "^window:"; then
    # Window preview - show window content
    window_target=$(echo "$selection" | awk '{print $2}')
    session_name=$(echo "$window_target" | cut -d':' -f1)
    window_index=$(echo "$window_target" | cut -d':' -f2)
    
    echo "=== WINDOW: $session_name:$window_index ==="
    echo ""
    tmux capture-pane -t "$window_target" -p 2>/dev/null | tail -30
    
else
    echo "Unknown selection format: $selection"
    exit 1
fi