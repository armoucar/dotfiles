import os
import re
import subprocess
import tempfile
from datetime import datetime
from typing import Optional, Dict

import click
import anyio
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock

from cli.app.command.video.cache import VideoCache


def parse_srt(srt_content: str) -> str:
    """Parse SRT subtitle content and extract clean text."""
    lines = srt_content.split("\n")
    text_lines = []

    for line in lines:
        line = line.strip()
        # Skip empty lines, sequence numbers, and timestamp lines
        if (
            not line
            or line.isdigit()
            or "-->" in line
            or re.match(r"^\d+:\d+:\d+", line)
        ):
            continue
        text_lines.append(line)

    # Join all text and clean up
    full_text = " ".join(text_lines)
    # Remove HTML tags if present
    full_text = re.sub(r"<[^>]+>", "", full_text)
    # Clean up extra whitespace
    full_text = re.sub(r"\s+", " ", full_text).strip()

    return full_text


def download_transcript(url: str) -> str:
    """Download video transcript using yt-dlp."""
    with tempfile.TemporaryDirectory() as temp_dir:
        transcript_path = os.path.join(temp_dir, "transcript")

        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--sub-format",
            "srt",
            "--skip-download",
            "--output",
            transcript_path,
            url,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            click.echo("✅ Successfully downloaded transcript")

            # Find the generated SRT file
            srt_files = [f for f in os.listdir(temp_dir) if f.endswith(".srt")]
            if not srt_files:
                raise click.ClickException("No subtitle file was generated")

            # Read the SRT content
            srt_path = os.path.join(temp_dir, srt_files[0])
            with open(srt_path, "r", encoding="utf-8") as f:
                srt_content = f.read()

            # Parse and return clean text
            return parse_srt(srt_content)

        except subprocess.CalledProcessError as e:
            click.echo(f"❌ yt-dlp error: {e.stderr}")
            raise click.ClickException(f"Failed to download transcript: {e}")


def get_video_title(url: str) -> str:
    """Get video title using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--get-title", url],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except:
        return "Unknown Video"


def display_help():
    """Display help for chat commands."""
    help_text = """
💡 Available commands:
  /help       - Show this help
  /exit       - End the chat session
  /quit       - Same as /exit
  /summary    - Generate a quick summary of the video
  /transcript - Show a sample of the transcript
  /clear      - Clear the screen
  
⌨️  Keyboard shortcuts:
  Ctrl+C      - Exit the chat
  Ctrl+D      - Exit the chat
  
Just type your question normally to chat about the video content!
"""
    click.echo(help_text)


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def select_from_history() -> Optional[Dict]:
    """Interactive fzf selection of cached videos."""
    cache = VideoCache()
    videos = cache.list_cached_videos()

    if not videos:
        click.echo("📭 No cached videos found")
        click.echo(
            "💡 Videos are cached automatically when you use 'dot video chat <url>'"
        )
        return None

    # Format for fzf display
    fzf_input = []
    for idx, (timestamp, description, url, title) in enumerate(videos):
        # Parse timestamp and format nicely
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = timestamp[:16]  # Fallback

        # Limit title and description to 60 characters, pad to create table-style columns
        if len(title) > 60:
            truncated_title = title[:57] + "..."
        else:
            truncated_title = title.ljust(60)  # Pad with spaces to 60 chars

        if len(description) > 60:
            truncated_description = description[:57] + "..."
        else:
            truncated_description = description.ljust(60)  # Pad with spaces to 60 chars

        # Format: "2024-01-27 14:30 | https://youtube.com/... | Video Title (padded) | AI Description (padded)"
        display = (
            f"{formatted_time} | {url} | {truncated_title} | {truncated_description}"
        )
        fzf_input.append(f"{idx}:{display}")

    # Create temp file for fzf input
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("\n".join(fzf_input))
        tmp_path = tmp.name

    try:
        # Check if fzf is available
        try:
            subprocess.run(["fzf", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            click.echo("❌ fzf is not installed. Please install it first:")
            click.echo("   brew install fzf  # macOS")
            click.echo("   apt install fzf   # Ubuntu/Debian")
            return None

        # Launch fzf with proper options
        fzf_cmd = [
            "fzf",
            "--height",
            "70%",
            "--reverse",  # Most recent at top
            "--no-sort",  # Keep our timestamp ordering
            "--header",
            f"Select a video (timestamp | url | title | description) • {len(videos)} total",
            "--prompt",
            "🎥 Video> ",
        ]

        with open(tmp_path, "r") as tmp_file:
            result = subprocess.run(
                fzf_cmd, stdin=tmp_file, capture_output=True, text=True
            )

        if result.returncode == 0 and result.stdout.strip():
            # Parse selection
            try:
                selected_idx = int(result.stdout.split(":")[0])
                selected_video = videos[selected_idx]

                # Load full transcript data
                cached_data = cache.get_full_cached_data(selected_video[2])  # url
                if cached_data:
                    return cached_data
                else:
                    click.echo("❌ Could not load cached data for selected video")
                    return None

            except (ValueError, IndexError) as e:
                click.echo(f"❌ Error parsing selection: {e}")
                return None
        else:
            # User cancelled or error
            return None

    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass

    return None


async def interactive_chat(
    transcript: str, video_title: str, options: ClaudeCodeOptions
):
    """Run the interactive chat session with Claude."""

    # Create system prompt with video context
    system_prompt = f"""You are an AI assistant helping users understand and discuss video content.
You have access to the complete transcript of the video they're asking about.

VIDEO TITLE: {video_title}

VIDEO TRANSCRIPT:
{transcript}

Your role:
- Answer questions about the video content
- Provide insights and analysis based on the transcript
- Quote relevant parts when helpful (but don't over-quote)
- Maintain conversational context
- Be concise but informative
- If asked about something not in the transcript, acknowledge the limitation

Guidelines:
- Keep responses conversational and engaging
- Use examples from the video when relevant
- Be helpful and accurate based on the available content
"""

    # Update options with system prompt
    options.system_prompt = system_prompt

    try:
        # Welcome message
        click.echo(
            f"\n🎬 Ready to chat about: {click.style(video_title, fg='blue', bold=True)}"
        )
        click.echo(f"📝 Transcript loaded ({len(transcript.split())} words)")
        click.echo(
            f"💬 Type your questions or use {click.style('/help', fg='yellow')} for commands"
        )
        click.echo(
            f"🚪 Type {click.style('/exit', fg='red')} or press {click.style('Ctrl+C/Ctrl+D', fg='red')} to exit"
        )
        click.echo("=" * 60)

        while True:
            try:
                # Get user input
                try:
                    user_input = input(
                        f"\n{click.style('You:', fg='green', bold=True)} "
                    ).strip()
                except (KeyboardInterrupt, EOFError):
                    # Handle Ctrl+C and Ctrl+D
                    click.echo("\n👋 Goodbye! Thanks for chatting about the video.")
                    break

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ["/exit", "/quit"]:
                    click.echo("\n👋 Goodbye! Thanks for chatting about the video.")
                    break
                elif user_input.lower() == "/help":
                    display_help()
                    continue
                elif user_input.lower() == "/clear":
                    clear_screen()
                    click.echo(f"🎬 Chatting about: {video_title}")
                    continue
                elif user_input.lower() == "/summary":
                    user_input = (
                        "Please provide a concise summary of this video's main points."
                    )
                elif user_input.lower() == "/transcript":
                    # Show first 300 words of transcript
                    words = transcript.split()
                    sample = " ".join(words[:300])
                    click.echo(f"\n📄 {click.style('Transcript sample:', fg='cyan')}")
                    click.echo(f"{sample}{'...' if len(words) > 300 else ''}\n")
                    continue

                # Send query to Claude using the query function
                click.echo(f"{click.style('Claude:', fg='blue', bold=True)} ", nl=False)

                # Use the query function and stream response
                response_started = False
                async for message in query(prompt=user_input, options=options):
                    if isinstance(message, AssistantMessage):
                        if not response_started:
                            response_started = True

                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(block.text, end="", flush=True)

                if response_started:
                    print()  # Add newline after response

            except KeyboardInterrupt:
                click.echo(
                    f"\n\n⚠️  Use {click.style('/exit', fg='red')} to end the chat gracefully."
                )
                continue
            except Exception as e:
                click.echo(f"\n❌ Error during chat: {str(e)}")
                continue

    except Exception as e:
        click.echo(f"❌ Failed to initialize chat session: {str(e)}")
        raise click.ClickException(f"Chat initialization failed: {str(e)}")


@click.command()
@click.argument("url", required=False)
@click.option(
    "--history", is_flag=True, help="Select from previously viewed videos using fzf"
)
@click.option(
    "--model",
    default="claude-3-5-sonnet-20241022",
    help="Claude model to use (default: claude-3-5-sonnet-20241022)",
)
@click.option(
    "--max-turns",
    default=50,
    help="Maximum number of conversation turns (default: 50)",
)
def chat(url: str, history: bool, model: str, max_turns: int):
    """
    Start an interactive chat about a video using its transcript.

    URL: YouTube video URL (optional if using --history)

    This command downloads the video transcript (or loads from cache) and starts
    an interactive chat session where you can ask questions about the video content.

    Use --history to select from previously viewed videos using fzf interface.

    Available in-chat commands:
    - /help: Show available commands
    - /exit or /quit: End the session
    - /summary: Generate a video summary
    - /transcript: Show transcript sample
    - /clear: Clear the screen

    Examples:
        dot video chat "https://www.youtube.com/watch?v=example"
        dot video chat --history  # Select from cached videos
        dot video chat "https://www.youtube.com/watch?v=example" --model claude-3-5-sonnet
        dot video chat --history --max-turns 20
    """
    try:
        cache = VideoCache()

        if history:
            # History mode: select from cached videos
            click.echo("📚 Loading video history...")
            selected = select_from_history()

            if not selected:
                click.echo("🚫 No video selected or no cached videos available")
                return

            url = selected["url"]
            transcript = selected["transcript"]
            video_title = selected["title"]

            click.echo(f"🎬 Selected: {click.style(video_title, fg='blue', bold=True)}")
            click.echo(f"📝 Description: {selected['description']}")

        else:
            # URL mode: download or load from cache
            if not url:
                raise click.ClickException(
                    "URL required unless using --history flag.\n"
                    "Usage: dot video chat <url> OR dot video chat --history"
                )

            # Check dependencies
            try:
                subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise click.ClickException(
                    "yt-dlp is not installed. Please install it first: pip install yt-dlp"
                )

            click.echo(f"🎥 Processing video: {url}")

            # Check cache first
            cached = cache.get_cached_transcript(url)

            if cached:
                click.echo("📦 Using cached transcript")
                transcript = cached["transcript"]
                video_title = cached["title"]
                click.echo(f"📝 Description: {cached['description']}")
            else:
                # Get video title
                click.echo("📋 Fetching video information...")
                video_title = get_video_title(url)

                # Download transcript
                click.echo("⬇️  Downloading transcript...")
                transcript = download_transcript(url)

                if not transcript.strip():
                    raise click.ClickException(
                        "No transcript content found. Video may not have subtitles available."
                    )

                # Cache the transcript
                cache.save_transcript(url, transcript, video_title)

        # Configure Claude Code options
        options = ClaudeCodeOptions(
            max_turns=max_turns,
            # Chat only - no tools needed
            allowed_tools=[],
            # Don't need file operations
            permission_mode=None,
        )

        # Start interactive chat
        anyio.run(interactive_chat, transcript, video_title, options)

    except click.ClickException:
        raise
    except KeyboardInterrupt:
        click.echo("\n⚠️ Operation cancelled by user.")
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}")
        raise click.ClickException(f"Failed to start video chat: {str(e)}")


if __name__ == "__main__":
    chat()
