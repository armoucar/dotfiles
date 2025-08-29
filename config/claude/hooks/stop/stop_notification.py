#!/usr/bin/env uv run python3
"""
Claude Code Stop Hook - Audio Notification

This hook plays an audio notification when Claude Code finishes responding.
Uses Submarine.aiff system sound.

Event: Stop
Single Responsibility: Audio notification playback
"""

import json
import sys
import subprocess


try:
    input_data = json.load(sys.stdin)

    # Play completion sound (Submarine.aiff)
    completion_sound = "/System/Library/Sounds/Submarine.aiff"

    try:
        subprocess.run(
            ["/usr/bin/afplay", completion_sound], check=True, capture_output=True
        )
        print("✓ Audio notification played (Submarine.aiff)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback - no audio available
        pass

except Exception as e:
    print(f"Error in notification hook: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
