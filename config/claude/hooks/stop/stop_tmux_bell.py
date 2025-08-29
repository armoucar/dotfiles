#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Tmux Bell Trigger

This hook triggers a tmux bell indicator when Claude Code finishes responding.
Only works when running inside a tmux session.

Event: Stop
Single Responsibility: Tmux bell notification
"""

import json
import sys
import subprocess
import os


def trigger_tmux_bell():
    """Trigger tmux bell indicator for current window."""
    if "TMUX" not in os.environ:
        return False

    try:
        # Get the terminal device for the current tmux pane
        tmux_pane = os.environ.get("TMUX_PANE", "unknown")
        result = subprocess.run(
            ["tmux", "display-message", "-p", "-t", tmux_pane, "#{pane_tty}"],
            capture_output=True,
            text=True,
            check=True,
        )
        pane_tty = result.stdout.strip()

        # Write bell directly to the terminal device using shell redirection
        subprocess.run(["sh", "-c", f'printf "\\007" > {pane_tty}'], check=True)
        return True
    except Exception:
        # Fallback methods if the above fails
        try:
            subprocess.run(["printf", "\007"], check=True)
            return True
        except Exception:
            try:
                sys.stdout.write("\007")
                sys.stdout.flush()
                return True
            except Exception:
                return False


try:
    input_data = json.load(sys.stdin)

    # Trigger tmux bell indicator
    tmux_triggered = trigger_tmux_bell()

    if tmux_triggered:
        print("✓ Tmux bell triggered")

except Exception as e:
    print(f"Error in tmux bell hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
