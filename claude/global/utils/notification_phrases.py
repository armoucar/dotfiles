#!/usr/bin/env uv run python3
"""
Natural notification phrases for Claude Code hooks.
Provides variety in how attention is requested from the user.
"""

NOTIFICATION_PHRASES = [
    "Attention needed",
    "Action blocked",
    "Permission needed",
    "Claude waiting",
    "Check this",
    "Input required",
]

# Voice options available in OpenAI TTS
AVAILABLE_VOICES = [
    "alloy",
    "ash",
    "ballad",
    "coral",
    "echo",
    "fable",
    "onyx",
    "sage",
    "shimmer"
]

def get_random_phrase():
    """Get a random notification phrase."""
    import random
    return random.choice(NOTIFICATION_PHRASES)

if __name__ == "__main__":
    print("Notification Phrases:")
    for i, phrase in enumerate(NOTIFICATION_PHRASES, 1):
        print(f"{i:2d}. {phrase}")

    print(f"\nAvailable Voices: {', '.join(AVAILABLE_VOICES)}")
    print(f"Total combinations: {len(NOTIFICATION_PHRASES)} × {len(AVAILABLE_VOICES)} = {len(NOTIFICATION_PHRASES) * len(AVAILABLE_VOICES)} audio files")