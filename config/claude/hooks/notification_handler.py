#!/usr/bin/env uv run python3
"""
Claude Code Notification Handler Hook

This hook is triggered on the "Notification" event when Claude Code needs to alert
the user. It uses voice notifications with session-consistent voices and random phrases.

Event: Notification
Output: macOS notification banner + Voice notification (session-specific)
"""

import json
import sys
import subprocess
import hashlib
import random
import os
from pathlib import Path

# Available voices (dynamically imported or defined)
AVAILABLE_VOICES = [
    "alloy",
    "ash",
    "ballad",
    "coral",
    "echo",
    "fable",
    "onyx",
    "sage",
    "shimmer",
]


def load_notification_config():
    """Load notification configuration from JSON file."""
    config_path = (
        Path.home()
        / ".oh-my-zsh"
        / "custom"
        / "config"
        / "claude"
        / "notification_config.json"
    )

    # Default configuration
    default_config = {
        "audio": {"type": "voice", "bell_file": "/System/Library/Sounds/Tink.aiff"}
    }

    try:
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        else:
            return default_config
    except Exception:
        return default_config


def get_session_voice(session_id: str) -> str:
    """
    Map a session UUID to a consistent voice using hash.
    Each session will always get the same voice.
    """
    hash_value = hashlib.md5(session_id.encode()).hexdigest()
    hash_int = int(hash_value[:8], 16)
    voice_index = hash_int % len(AVAILABLE_VOICES)  # Dynamic voice count
    return AVAILABLE_VOICES[voice_index]


def get_random_audio_file(voice: str) -> Path:
    """Get a random audio file for the given voice."""
    voice_dir = (
        Path.home()
        / ".oh-my-zsh"
        / "custom"
        / "config"
        / "claude"
        / "voice_notifications"
        / voice
    )

    if not voice_dir.exists():
        return None

    audio_files = list(voice_dir.glob("*.wav"))
    if not audio_files:
        return None

    return random.choice(audio_files)


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
    message = input_data.get("message", "Claude Code notification")

    # Get session ID directly from Claude Code input
    session_id = input_data.get("session_id", "default-session")

    # Load configuration
    config = load_notification_config()
    audio_type = config["audio"]["type"]
    bell_file = config["audio"]["bell_file"]

    # Trigger tmux bell indicator
    tmux_triggered = trigger_tmux_bell()

    # Play notification based on configuration
    try:
        if audio_type == "voice":
            # Map session to consistent voice
            voice = get_session_voice(session_id)
            audio_file = get_random_audio_file(voice)

            if audio_file and audio_file.exists():
                # Play the voice notification
                subprocess.run(
                    ["afplay", str(audio_file)], check=True, capture_output=True
                )
                cmd = f'display notification "{message}" with title "Claude Code ({voice})"'
                subprocess.run(
                    ["osascript", "-e", cmd], check=True, capture_output=True
                )
                tmux_status = " [tmux bell triggered]" if tmux_triggered else ""
                print(
                    f"✓ Played {voice} voice: {audio_file.name} (session: {session_id[:8]}...){tmux_status}"
                )
            else:
                # Fallback to bell if voice files missing
                subprocess.run(["afplay", bell_file], check=True, capture_output=True)
                cmd = f'display notification "{message}" with title "Claude Code"'
                subprocess.run(
                    ["osascript", "-e", cmd], check=True, capture_output=True
                )
                tmux_status = " [tmux bell triggered]" if tmux_triggered else ""
                print(
                    f"✓ Sent notification with bell sound (voice files not found){tmux_status}"
                )
        else:  # audio_type == 'bell'
            # Play configured bell sound
            subprocess.run(["afplay", bell_file], check=True, capture_output=True)
            cmd = f'display notification "{message}" with title "Claude Code"'
            subprocess.run(["osascript", "-e", cmd], check=True, capture_output=True)
            tmux_status = " [tmux bell triggered]" if tmux_triggered else ""
            print(f"✓ Sent notification with bell sound{tmux_status}")

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback for Linux or if audio fails
        try:
            subprocess.run(
                ["notify-send", "Claude Code", message], check=True, capture_output=True
            )
            print("✓ Sent Linux notification")
        except:
            print(f"🔔 Claude Code: {message}")

except Exception as e:
    print(f"Error sending notification: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation
