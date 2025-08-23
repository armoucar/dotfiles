#!/usr/bin/env uv run python3
"""
Voice notification handler for Claude Code hooks.
Maps session UUIDs to consistent voices and plays random phrase variations.
"""
import json
import sys
import subprocess
import hashlib
import random
from pathlib import Path

# Import voice options from notification phrases
sys.path.insert(0, str(Path(__file__).parent.parent))
from notification_phrases import AVAILABLE_VOICES

def get_session_voice(session_id: str) -> str:
    """
    Map a session UUID to a consistent voice using hash.
    Each session will always get the same voice.
    """
    # Create a hash of the session ID
    hash_value = hashlib.md5(session_id.encode()).hexdigest()
    # Convert first 8 chars of hash to integer
    hash_int = int(hash_value[:8], 16)
    # Map to voice index (0-8 for 9 voices)
    voice_index = hash_int % len(AVAILABLE_VOICES)
    return AVAILABLE_VOICES[voice_index]

def get_random_audio_file(voice: str) -> Path:
    """
    Get a random audio file for the given voice.
    Returns the path to a random notification audio file.
    """
    voice_dir = Path(__file__).parent.parent / "voice_notifications" / voice
    
    if not voice_dir.exists():
        return None
    
    # Get all .wav files in the voice directory
    audio_files = list(voice_dir.glob("*.wav"))
    
    if not audio_files:
        return None
    
    # Return a random audio file
    return random.choice(audio_files)

def play_voice_notification(session_id: str, message: str = None):
    """
    Play a voice notification for the given session.
    Uses consistent voice per session with random phrase variation.
    """
    try:
        # Get the consistent voice for this session
        voice = get_session_voice(session_id)
        
        # Get a random audio file for this voice
        audio_file = get_random_audio_file(voice)
        
        if audio_file and audio_file.exists():
            # Play the audio file
            subprocess.run(['afplay', str(audio_file)], 
                         check=True, capture_output=True)
            
            # Also show visual notification if message provided
            if message:
                cmd = f'display notification "{message}" with title "Claude Code ({voice})"'
                subprocess.run(['osascript', '-e', cmd], 
                             check=True, capture_output=True)
            
            print(f"✓ Played {voice} voice notification: {audio_file.name}")
            return True
        else:
            print(f"⚠️ No audio files found for voice: {voice}")
            return False
            
    except Exception as e:
        print(f"Error playing voice notification: {e}", file=sys.stderr)
        return False

def main():
    """Main entry point for the notification handler."""
    try:
        input_data = json.load(sys.stdin)
        
        # Get session ID and message
        session_id = input_data.get('session_id', 'default')
        message = input_data.get('message', 'Claude Code notification')
        
        # Play voice notification
        success = play_voice_notification(session_id, message)
        
        if not success:
            # Fallback to simple notification
            cmd = f'display notification "{message}" with title "Claude Code"'
            subprocess.run(['osascript', '-e', cmd], 
                         check=True, capture_output=True)
            print("✓ Sent fallback notification")
    
    except Exception as e:
        print(f"Error in notification handler: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block the operation

if __name__ == "__main__":
    main()