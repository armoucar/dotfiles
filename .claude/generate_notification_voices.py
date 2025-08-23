#!/usr/bin/env uv run python3
"""
Generate natural voice notifications for Claude Code hooks.
Creates audio files for all voice/phrase combinations using OpenAI TTS API.

Usage:
  uv run .claude/generate_notification_voices.py           # Generate all voices
  uv run .claude/generate_notification_voices.py alloy     # Generate only alloy voice
"""

import os
import sys
import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from notification_phrases import NOTIFICATION_PHRASES, AVAILABLE_VOICES

# Initialize OpenAI client
client = AsyncOpenAI()

async def generate_voice_file(voice: str, phrase: str, phrase_index: int, base_dir: Path):
    """Generate a single voice file for a phrase."""
    try:
        # Create voice directory
        voice_dir = base_dir / voice
        voice_dir.mkdir(exist_ok=True)
        
        # Create filename
        filename = f"notification_{phrase_index:02d}.wav"
        file_path = voice_dir / filename
        
        print(f"Generating {voice}/{filename}...")
        
        # Generate TTS audio with explicit file writing
        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=phrase,
            instructions="Speak with energy and urgency - friendly but fast-paced, like a productive work colleague who needs a quick response. Sound proactive and focused.",
            response_format="wav"
        ) as response:
            # Write to file with explicit handling like in test script
            with open(file_path, 'wb') as f:
                async for chunk in response.iter_bytes():
                    f.write(chunk)
        
        # Verify file exists and has content
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ Generated {voice}/{filename} - {size} bytes")
            return True
        else:
            print(f"❌ File not found: {voice}/{filename}")
            return False
        
    except Exception as e:
        print(f"❌ Error generating {voice}/{filename}: {e}")
        return False

async def generate_voices(target_voice=None):
    """Generate voice notifications for specified voice or all voices."""
    # Create base directory for voice files
    base_dir = Path(".claude/voice_notifications")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which voices to generate
    if target_voice:
        if target_voice not in AVAILABLE_VOICES:
            print(f"❌ Error: '{target_voice}' is not a valid voice.")
            print(f"Available voices: {', '.join(AVAILABLE_VOICES)}")
            return
        voices_to_generate = [target_voice]
        print(f"Generating {len(NOTIFICATION_PHRASES)} phrases for {target_voice} voice = {len(NOTIFICATION_PHRASES)} files")
    else:
        voices_to_generate = AVAILABLE_VOICES
        print(f"Generating {len(NOTIFICATION_PHRASES)} phrases × {len(AVAILABLE_VOICES)} voices = {len(NOTIFICATION_PHRASES) * len(AVAILABLE_VOICES)} files")
        print("This may take several minutes...")
    
    print()
    
    # Generate all combinations
    tasks = []
    for phrase_index, phrase in enumerate(NOTIFICATION_PHRASES, 1):
        for voice in voices_to_generate:
            task = generate_voice_file(voice, phrase, phrase_index, base_dir)
            tasks.append(task)
    
    # Execute all tasks with some concurrency control
    semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
    
    async def limited_task(task):
        async with semaphore:
            return await task
    
    results = await asyncio.gather(*[limited_task(task) for task in tasks])
    
    successful = sum(results)
    total = len(results)
    
    print(f"\n✅ Generation complete: {successful}/{total} files created successfully")
    
    # Create/update index file
    create_voice_index(base_dir)

def create_voice_index(base_dir: Path):
    """Create an index file showing all generated voices."""
    index_file = base_dir / "README.md"
    
    with open(index_file, 'w') as f:
        f.write("# Claude Code Voice Notifications\n\n")
        f.write("Generated natural voice notifications for Claude Code hooks.\n\n")
        f.write("## Structure\n\n")
        
        for voice in AVAILABLE_VOICES:
            f.write(f"### {voice.title()} Voice\n")
            voice_dir = base_dir / voice
            if voice_dir.exists():
                files = sorted(voice_dir.glob("*.wav"))
                for file in files:
                    phrase_num = int(file.stem.split('_')[1])
                    phrase = NOTIFICATION_PHRASES[phrase_num - 1]
                    f.write(f"- `{file.name}`: \"{phrase}\"\n")
            f.write("\n")
        
        f.write("## Usage\n\n")
        f.write("These audio files are used by the notification hook to provide natural voice alerts.\n")
        f.write("The hook randomly selects a voice and phrase combination for variety.\n")
    
    print(f"✓ Created index file: {index_file}")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not found")
        print("Please set your OpenAI API key before running this script")
        exit(1)
    
    # Parse command line arguments
    target_voice = None
    if len(sys.argv) > 1:
        target_voice = sys.argv[1]
    
    print("🎙️  Claude Code Voice Notification Generator")
    print("=" * 50)
    
    if target_voice:
        print(f"Target voice: {target_voice}")
    else:
        print("Generating all voices")
    
    # Run generation
    asyncio.run(generate_voices(target_voice))