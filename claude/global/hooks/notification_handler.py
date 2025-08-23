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
    "alloy", "ash", "ballad", "coral", "echo", 
    "fable", "onyx", "sage", "shimmer"
]

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
    voice_dir = Path(__file__).parent.parent / "voice_notifications" / voice
    
    if not voice_dir.exists():
        return None
    
    audio_files = list(voice_dir.glob("*.wav"))
    if not audio_files:
        return None
        
    return random.choice(audio_files)

def trigger_tmux_activity():
    """Trigger tmux activity indicator for current window."""
    if 'TMUX' not in os.environ:
        return False
    
    try:
        # Send both bell and activity to ensure flags are set
        sys.stdout.write('\a')  # Bell
        sys.stdout.flush()
        
        # Also write some output to trigger monitor-activity
        sys.stdout.write('\n')  # Newline triggers activity
        sys.stdout.flush()
        
        return True
    except Exception:
        return False

try:
    input_data = json.load(sys.stdin)
    message = input_data.get('message', 'Claude Code notification')
    
    # Get session ID directly from Claude Code input
    session_id = input_data.get('session_id', 'default-session')
    
    # Map session to consistent voice
    voice = get_session_voice(session_id)
    
    # Get random audio file for this voice
    audio_file = get_random_audio_file(voice)
    
    # Trigger tmux activity indicator
    tmux_triggered = trigger_tmux_activity()
    
    # Try to play voice notification
    try:
        if audio_file and audio_file.exists():
            # Play the voice notification
            subprocess.run(['afplay', str(audio_file)], 
                         check=True, capture_output=True)
            
            # Also show visual notification with voice name
            cmd = f'display notification "{message}" with title "Claude Code ({voice})"'
            subprocess.run(['osascript', '-e', cmd], check=True, capture_output=True)
            
            tmux_status = " [tmux activity triggered]" if tmux_triggered else ""
            print(f"✓ Played {voice} voice: {audio_file.name} (session: {session_id[:8]}...){tmux_status}")
        else:
            # Fallback to Tink sound if no voice files
            cmd = f'display notification "{message}" with title "Claude Code"'
            subprocess.run(['osascript', '-e', cmd], check=True, capture_output=True)
            subprocess.run(['afplay', '/System/Library/Sounds/Tink.aiff'], 
                         check=True, capture_output=True)
            tmux_status = " [tmux activity triggered]" if tmux_triggered else ""
            print(f"✓ Sent notification with Tink sound (voice files not found for {voice}){tmux_status}")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback for Linux or if audio fails
        try:
            subprocess.run(['notify-send', 'Claude Code', message], 
                         check=True, capture_output=True)
            print("✓ Sent Linux notification")
        except:
            print(f"🔔 Claude Code: {message}")

except Exception as e:
    print(f"Error sending notification: {str(e)}", file=sys.stderr)
    sys.exit(0)  # Don't block the operation