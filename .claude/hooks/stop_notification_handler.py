#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Completion Notification

This hook is triggered on the "Stop" event when Claude Code finishes responding.
It plays a completion sound to indicate the task is done.

Event: Stop  
Output: Audio notification (Glass.aiff)
"""
import json
import sys
import subprocess
import os

def trigger_tmux_bell():
    """Trigger tmux bell indicator for current window."""
    if 'TMUX' not in os.environ:
        return False
    
    try:
        # Get the terminal device for the current tmux pane
        tmux_pane = os.environ.get('TMUX_PANE', 'unknown')
        result = subprocess.run(['tmux', 'display-message', '-p', '-t', tmux_pane, '#{pane_tty}'], 
                              capture_output=True, text=True, check=True)
        pane_tty = result.stdout.strip()
        
        # Write bell directly to the terminal device using shell redirection
        subprocess.run(['sh', '-c', f'printf "\\007" > {pane_tty}'], check=True)
        return True
    except Exception:
        # Fallback methods if the above fails
        try:
            subprocess.run(['printf', '\007'], check=True)
            return True
        except Exception:
            try:
                sys.stdout.write('\007')
                sys.stdout.flush()
                return True
            except Exception:
                return False

try:
    input_data = json.load(sys.stdin)
    
    # Trigger tmux bell indicator
    tmux_triggered = trigger_tmux_bell()
    
    # Play completion sound (Glass.aiff instead of Tink.aiff)
    completion_sound = '/System/Library/Sounds/Glass.aiff'
    
    try:
        subprocess.run(['afplay', completion_sound], check=True, capture_output=True)
        tmux_status = " [tmux bell triggered]" if tmux_triggered else ""
        print(f"✓ Claude Code completed - played Glass.aiff{tmux_status}")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback - just print completion message
        print("✓ Claude Code completed")

except Exception as e:
    print(f"Error in stop hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation