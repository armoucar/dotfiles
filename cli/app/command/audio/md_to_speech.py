import os
import asyncio
import re
import subprocess
import tempfile
import hashlib
import json
from pathlib import Path
from textwrap import dedent
from time import time
import click
from openai import AsyncOpenAI, OpenAI


@click.command()
@click.argument(
    "markdown_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "--voice",
    default="alloy",
    help="Voice to use for speech (alloy, echo, fable, onyx, nova, shimmer, coral)",
)
@click.option("--model", default="gpt-4o-mini-tts", help="Model to use for TTS")
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path (defaults to tmp folder with input filename)",
)
@click.option(
    "--language",
    default="ptbr",
    help="Language to generate content in (e.g., en, ptbr)",
)
@click.option(
    "--no-cache", is_flag=True, help="Skip using cached results even if available"
)
@click.option("--debug", is_flag=True, help="Show detailed debugging information")
@click.option(
    "--keypoints",
    is_flag=True,
    help="Also extract and vocalize key points from the document",
)
def md_to_speech(
    markdown_file, voice, model, output, language, no_cache, debug, keypoints
):
    """Convert a markdown file to speech using OpenAI's text-to-speech API.

    This command takes a markdown file, sends it to OpenAI to transform into
    a more listenable format, then saves it as an MP3 file.

    Results are cached for faster subsequent runs with the same parameters.

    When --keypoints is specified, also extracts top 5 key points and 5 unanswered
    points from the document and creates separate audio files for them.
    """
    click.echo(f"Processing {markdown_file}...")

    # Read the markdown file
    with open(markdown_file, "r") as f:
        markdown_content = f.read()

    if debug:
        click.echo(
            f"Markdown content hash: {hashlib.md5(markdown_content.encode()).hexdigest()}"
        )

    # Preprocess the markdown content to remove image data
    markdown_content = preprocess_markdown(markdown_content)

    # Calculate file hash for cache consistency
    file_hash = hashlib.md5(markdown_content.encode()).hexdigest()

    if debug:
        click.echo(f"Preprocessed content hash: {file_hash}")

    # Get the cache directory
    cache_dir = get_cache_dir(debug)

    # Generate a key for the transformed text
    transform_key = f"{file_hash}|{language}"
    transform_cache_key = hashlib.md5(transform_key.encode()).hexdigest()
    transform_cache_path = os.path.join(
        cache_dir,
        transform_cache_key[:2],
        transform_cache_key[2:4],
        f"{transform_cache_key}.txt",
    )

    # Check if we have a cached transformed text
    if not no_cache and os.path.exists(transform_cache_path):
        if debug:
            click.echo(f"Using cached transformed text from {transform_cache_path}")
        with open(transform_cache_path, "r") as f:
            listenable_text = f.read()
    else:
        # Step 1: Transform the markdown to a more listenable format
        listenable_text = transform_markdown_to_speech(markdown_content, language)

        # Cache the transformed text
        os.makedirs(os.path.dirname(transform_cache_path), exist_ok=True)
        with open(transform_cache_path, "w") as f:
            f.write(listenable_text)
        if debug:
            click.echo(f"Cached transformed text to {transform_cache_path}")

    # Create a temp directory for outputs
    temp_dir = tempfile.mkdtemp(prefix="md_to_speech_", dir="/tmp")

    # Save the text content to a temporary file
    text_file = os.path.join(temp_dir, "text_content.txt")
    with open(text_file, "w") as f:
        f.write(listenable_text)

    # Set output path
    if output:
        output_path = output
    else:
        base_filename = os.path.splitext(os.path.basename(markdown_file))[0]
        output_path = os.path.join(temp_dir, f"{base_filename}.mp3")

    # Step 2: Split the text into manageable chunks
    text_chunks = split_text_into_chunks(listenable_text)
    click.echo(f"Split text into {len(text_chunks)} chunks")

    # Step 3: Process each chunk and concatenate the results
    asyncio.run(
        process_text_chunks(
            text_chunks,
            voice,
            model,
            output_path,
            transform_cache_key,
            language,
            no_cache,
            debug,
        )
    )

    # Process key points if requested
    if keypoints:
        click.echo("\nExtracting key points from document...")
        keypoints_text = extract_document_keypoints(markdown_content, language)

        # Save the keypoints text
        keypoints_file = os.path.join(temp_dir, "keypoints.txt")
        with open(keypoints_file, "w") as f:
            f.write(keypoints_text)

        # Create a keypoints audio file
        keypoints_audio_path = os.path.join(temp_dir, "keypoints.mp3")

        # Process keypoints text for audio
        keypoints_chunks = split_text_into_chunks(keypoints_text)
        click.echo(f"Split keypoints into {len(keypoints_chunks)} chunks")

        # Generate a unique key for keypoints
        keypoints_key = f"{file_hash}|keypoints|{language}"
        keypoints_cache_key = hashlib.md5(keypoints_key.encode()).hexdigest()

        # Generate audio for keypoints
        asyncio.run(
            process_text_chunks(
                keypoints_chunks,
                voice,
                model,
                keypoints_audio_path,
                keypoints_cache_key,
                language,
                no_cache,
                debug,
            )
        )

        # Format keypoints as a list and save as text only (no audio)
        click.echo("Formatting keypoints as a list...")
        keypoints_list = format_keypoints_as_list(keypoints_text, language)
        keypoints_list_file = os.path.join(temp_dir, "keypoints_list.txt")
        with open(keypoints_list_file, "w") as f:
            f.write(keypoints_list)

    # Print paths in clickable format
    click.echo("\nOutput files:")
    click.echo(f"Audio file: {os.path.abspath(output_path)}")
    click.echo(f"Text file: {os.path.abspath(text_file)}")
    if keypoints:
        click.echo(f"Keypoints audio: {os.path.abspath(keypoints_audio_path)}")
        click.echo(f"Keypoints text: {os.path.abspath(keypoints_file)}")
        click.echo(f"Keypoints list: {os.path.abspath(keypoints_list_file)}")
    click.echo(f"Temp folder: {os.path.abspath(temp_dir)}")

    # Run a 'open' command to open the output folder
    subprocess.run(["open", temp_dir])

    # Open the mp3 file with VLC
    # Start VLC with the desired playback rate and pause it after a second
    subprocess.run(
        ["/Applications/VLC.app/Contents/MacOS/VLC", "--rate=1.5", output_path],
        shell=False,
    )


def split_text_into_chunks(text, max_chunk_size=3000):
    """Split text into chunks of maximum size, splitting at sentence boundaries."""
    chunks = []
    current_chunk = ""

    # Split text into sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)

    for sentence in sentences:
        # If adding this sentence would exceed max size, start a new chunk
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


async def process_text_chunks(
    chunks, voice, model, output_path, transform_key, language, no_cache, debug
):
    """Process each text chunk, generate audio, and combine them."""
    temp_dir = tempfile.mkdtemp(prefix="md_to_speech_chunks_", dir="/tmp")
    chunk_files = []

    # Process each chunk
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(temp_dir, f"chunk_{i:03d}.mp3")
        chunk_files.append(chunk_file)

        # Generate a cache key for this chunk using the transform key for consistency
        cache_key = generate_cache_key(transform_key, i, voice, model)

        if debug:
            click.echo(f"Chunk {i} length: {len(chunk)}")
            click.echo(f"Generated cache key: {cache_key}")

        cache_dir = get_cache_dir(debug)

        # We don't need text cache path here, but the function returns both
        _, audio_cache_path = get_cache_paths(cache_dir, cache_key)

        if debug:
            click.echo(f"Cache path: {audio_cache_path}")

        # Check if we have a cached version of this chunk
        if not no_cache and os.path.exists(audio_cache_path):
            click.echo(f"Using cached audio for chunk {i + 1}/{len(chunks)}")
            # Copy from cache to temp file
            with open(audio_cache_path, "rb") as src, open(chunk_file, "wb") as dst:
                dst.write(src.read())
        else:
            click.echo(f"Generating audio for chunk {i + 1}/{len(chunks)}")
            # Generate audio for this chunk
            await save_speech_to_file(chunk, voice, model, chunk_file)

            # Create cache directory if it doesn't exist
            os.makedirs(os.path.dirname(audio_cache_path), exist_ok=True)

            # Cache this chunk
            try:
                with open(chunk_file, "rb") as src, open(audio_cache_path, "wb") as dst:
                    dst.write(src.read())
                if debug:
                    click.echo(f"Cached audio at {audio_cache_path}")
            except Exception as e:
                click.echo(f"Error caching audio: {e}")

            # Save cache metadata
            cache_info = {
                "chunk_index": i,
                "voice": voice,
                "model": model,
                "language": language,
                "timestamp": asyncio.get_event_loop().time(),
                "chunk_length": len(chunk),
                "transform_key": transform_key,
            }
            save_cache_metadata(cache_dir, cache_key, cache_info, debug)

    # Combine all chunks into the final output file
    combine_audio_files(chunk_files, output_path)


def combine_audio_files(input_files, output_file):
    """Combine multiple MP3 files into a single file."""
    click.echo("Combining audio chunks...")

    # Create an empty output file
    with open(output_file, "wb") as outfile:
        # Append each input file
        for infile_path in input_files:
            with open(infile_path, "rb") as infile:
                outfile.write(infile.read())


def preprocess_markdown(content):
    """Remove base64 encoded images and other large data from markdown content."""
    # Remove base64 image data references
    content = re.sub(r"\[.*?\]:\s*<data:image/[^>]+base64,[^>]+>", "", content)

    # Remove inline base64 images
    content = re.sub(
        r"!\[.*?\]\(data:image/[^)]+base64,[^)]+\)", "[Image removed]", content
    )

    # Remove other potential large embedded data
    content = re.sub(r"<img[^>]*?base64,[^>]+>", "[Image removed]", content)

    return content


def transform_markdown_to_speech(markdown_content, language="ptbr"):
    """Transform markdown content to a more listenable format using OpenAI."""
    client = OpenAI()

    # Get language specific instructions
    language_instruction = get_language_instruction(language)

    response = client.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=[
            {
                "role": "system",
                "content": TO_READABLE_TEXT_PROMPT + language_instruction,
            },
            {
                "role": "user",
                "content": f"Here is the markdown content:\n\n{markdown_content}",
            },
        ],
    )

    return response.choices[0].message.content


def get_language_instruction(language_code):
    """Get language-specific instructions for the AI model."""
    language_map = {
        "ptbr": "\n\nImportante: Gere o texto em português brasileiro (pt-BR).",
        "en": "\n\nImportant: Generate the text in English (en).",
        "es": "\n\nImportante: Genera el texto en español (es).",
        "fr": "\n\nImportant: Générez le texte en français (fr).",
        "de": "\n\nWichtig: Generieren Sie den Text auf Deutsch (de).",
    }

    return language_map.get(
        language_code.lower(), f"\n\nImportant: Generate the text in {language_code}."
    )


async def save_speech_to_file(text, voice, model, output_path):
    """Save the speech to a file using streaming API."""
    client = AsyncOpenAI()

    async with client.audio.speech.with_streaming_response.create(
        model=model, voice=voice, input=text
    ) as response:
        with open(output_path, "wb") as f:
            async for chunk in response.iter_bytes():
                f.write(chunk)


def generate_cache_key(transform_key, chunk_index, voice, model):
    """Generate a unique cache key based on input parameters."""
    # Include all relevant parameters in the key to ensure uniqueness and consistency
    key_string = f"{transform_key}|{chunk_index}|{voice}|{model}"
    return hashlib.md5(key_string.encode()).hexdigest()


def get_cache_dir(debug=False):
    """Get the cache directory path."""
    cache_dir = os.path.expanduser("~/.cache/md_to_speech")
    try:
        os.makedirs(cache_dir, exist_ok=True)
        # Test if we can write to this directory
        test_file = os.path.join(cache_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        if debug:
            click.echo(f"Cache directory: {cache_dir}")
    except Exception as e:
        click.echo(f"Warning: Cannot write to cache directory: {e}")
        # Fall back to temp directory
        cache_dir = os.path.join(tempfile.gettempdir(), "md_to_speech_cache")
        os.makedirs(cache_dir, exist_ok=True)
        click.echo(f"Using fallback cache directory: {cache_dir}")
    return cache_dir


def get_cache_paths(cache_dir, cache_key):
    """Get the paths for cached text and audio files."""
    # Create subdirectories based on first few characters of cache key
    subdir = os.path.join(cache_dir, cache_key[:2], cache_key[2:4])
    os.makedirs(subdir, exist_ok=True)

    text_path = os.path.join(subdir, f"{cache_key}.txt")
    audio_path = os.path.join(subdir, f"{cache_key}.mp3")

    return text_path, audio_path


def save_cache_metadata(cache_dir, cache_key, metadata, debug=False):
    """Save metadata about the cached files."""
    subdir = os.path.join(cache_dir, cache_key[:2], cache_key[2:4])
    metadata_path = os.path.join(subdir, f"{cache_key}.json")

    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
        if debug:
            click.echo(f"Saved metadata to {metadata_path}")
    except Exception as e:
        click.echo(f"Error saving cache metadata: {e}")


def extract_document_keypoints(markdown_content, language="ptbr"):
    """Extract the top 5 key points and bottom 5 unanswered points from the document."""
    client = OpenAI()

    # Get language specific instructions
    language_instruction = get_language_instruction(language)

    response = client.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=[
            {
                "role": "system",
                "content": KEYPOINTS_EXTRACTION_PROMPT + language_instruction,
            },
            {
                "role": "user",
                "content": f"Here is the markdown content:\n\n{markdown_content}",
            },
        ],
    )

    return response.choices[0].message.content


def format_keypoints_as_list(keypoints_text, language="ptbr"):
    """Format the extracted keypoints into a clean list format."""
    client = OpenAI()

    # Get language specific instructions
    language_instruction = get_language_instruction(language)

    response = client.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=[
            {
                "role": "system",
                "content": KEYPOINTS_LIST_FORMAT_PROMPT + language_instruction,
            },
            {
                "role": "user",
                "content": f"Here are the extracted keypoints:\n\n{keypoints_text}",
            },
        ],
    )

    return response.choices[0].message.content


TO_READABLE_TEXT_PROMPT = dedent(
    """
    You're provided with a Markdown document containing text, headings, and images. Transform it into a series of clear, listenable paragraphs, structured specifically for a listener instead of a reader:

    - **Content:** Focus on the core content of the document, skipping metadata like author, date, approvers, etc.

    - **Details:** Be descriptive and include all details from the original document.

    - **Structure:** Remove markdown formatting, headings, bullet points, and lists. Instead, structure the document into flowing paragraphs suitable for spoken delivery.

    - **Perspective:** Briefly indicate when there's an accompanying image that a listener cannot see (e.g., "An image accompanies this text").

    - **Maintain Originality:** Retain the original wording and meaning as closely as possible, adjusting minimally only to clarify references for audio context.
    """
)

KEYPOINTS_EXTRACTION_PROMPT = dedent(
    """
    You're provided with a Markdown document. Analyze it and extract:

    1. The 5 most important key points from the document
    2. The 5 least addressed or unanswered points/questions raised in the document

    Format your response in a clear, listenable way:

    Begin with: "Here are the 5 most important points from the document:"
    [List the 5 main points in clear, concise paragraphs]

    Then: "Here are 5 points or questions that were not fully addressed in the document:"
    [List the 5 unanswered or insufficiently addressed points in clear, concise paragraphs]

    Make each point detailed enough to be useful and substantive. Structure your response as flowing paragraphs suitable for spoken delivery, not as bullet points.
    """
)

KEYPOINTS_LIST_FORMAT_PROMPT = dedent(
    """
    You'll receive a text containing key points extracted from a document, with positive points and unanswered/negative points.

    Your task is to format these points into clearly numbered lists that are easy to read.

    Format your response as follows:

    ## TOP 5 KEY POINTS:
    1. [First key point in a concise format]
    2. [Second key point in a concise format]
    ...and so on

    ## 5 POINTS REQUIRING ATTENTION:
    1. [First unanswered point in a concise format]
    2. [Second unanswered point in a concise format]
    ...and so on

    Make each point concise but complete. Maintain the original meaning but optimize for readability in list format.
    """
)


if __name__ == "__main__":
    md_to_speech()
