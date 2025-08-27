import os
import json
import hashlib
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import click
from openai import OpenAI


class VideoCache:
    """Manages caching of video transcripts and metadata."""

    def __init__(self):
        self.cache_dir = os.path.expanduser("~/.cache/video_transcripts")
        self.transcripts_dir = os.path.join(self.cache_dir, "transcripts")
        self.metadata_file = os.path.join(self.cache_dir, "metadata.json")
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directories exist."""
        try:
            os.makedirs(self.transcripts_dir, exist_ok=True)
            # Test write access
            test_file = os.path.join(self.cache_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception:
            # Fall back to temp directory
            self.cache_dir = os.path.join(
                tempfile.gettempdir(), "video_transcripts_cache"
            )
            self.transcripts_dir = os.path.join(self.cache_dir, "transcripts")
            self.metadata_file = os.path.join(self.cache_dir, "metadata.json")
            os.makedirs(self.transcripts_dir, exist_ok=True)
            click.echo(f"Warning: Using fallback cache directory: {self.cache_dir}")

    def _generate_video_id(self, url: str) -> str:
        """Generate unique ID for video based on URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _load_metadata(self) -> Dict:
        """Load metadata from cache file."""
        if not os.path.exists(self.metadata_file):
            return {"videos": []}

        try:
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"videos": []}

    def _save_metadata(self, metadata: Dict):
        """Save metadata to cache file."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        except IOError as e:
            click.echo(f"Warning: Could not save cache metadata: {e}")

    def generate_description(self, transcript: str, title: str) -> str:
        """Generate a concise description using OpenAI."""
        try:
            client = OpenAI()

            # Use first 2000 chars of transcript for efficiency
            content_sample = transcript[:2000]

            prompt = f"""Generate a very concise 5-10 word description of this video's main topic/content.
Focus on the key subject matter, not generic phrases.

Title: {title}
Content sample: {content_sample}

Examples of good descriptions:
- "Advanced Claude Code hooks and techniques"
- "Python async programming fundamentals"
- "Machine learning model optimization strategies"
- "JavaScript React performance best practices"

Generate ONLY the concise description, no extra text:"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.3,
            )

            description = response.choices[0].message.content.strip()
            # Remove quotes if present and limit length
            description = description.strip("\"'").strip()

            # Fallback if too long or empty
            if len(description) > 80 or len(description) < 10:
                # Extract key words from title
                words = title.split()[:8]
                description = " ".join(words).lower()

            return description

        except Exception as e:
            click.echo(f"Warning: Could not generate description: {e}")
            # Fallback to truncated title
            return title[:50] + "..." if len(title) > 50 else title

    def save_transcript(self, url: str, transcript: str, title: str) -> str:
        """Save transcript and metadata to cache."""
        video_id = self._generate_video_id(url)
        video_dir = os.path.join(self.transcripts_dir, video_id)

        try:
            os.makedirs(video_dir, exist_ok=True)

            # Save transcript
            transcript_path = os.path.join(video_dir, "transcript.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)

            # Generate and save description
            click.echo("🧠 Generating video description...")
            description = self.generate_description(transcript, title)

            description_path = os.path.join(video_dir, "description.txt")
            with open(description_path, "w", encoding="utf-8") as f:
                f.write(description)

            # Save video metadata
            video_metadata = {
                "url": url,
                "title": title,
                "description": description,
                "transcript_path": transcript_path,
                "word_count": len(transcript.split()),
            }

            metadata_path = os.path.join(video_dir, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(video_metadata, f, indent=2)

            # Update global metadata
            metadata = self._load_metadata()

            # Remove existing entry if present
            metadata["videos"] = [v for v in metadata["videos"] if v["id"] != video_id]

            # Add new entry
            video_entry = {
                "id": video_id,
                "url": url,
                "title": title,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "word_count": len(transcript.split()),
                "last_accessed": datetime.now().isoformat(),
            }
            metadata["videos"].insert(0, video_entry)  # Most recent first

            self._save_metadata(metadata)

            click.echo(f"💾 Cached transcript: {description}")
            return video_id

        except Exception as e:
            click.echo(f"Warning: Could not save to cache: {e}")
            return ""

    def get_cached_transcript(self, url: str) -> Optional[Dict]:
        """Get cached transcript if it exists."""
        video_id = self._generate_video_id(url)
        video_dir = os.path.join(self.transcripts_dir, video_id)
        transcript_path = os.path.join(video_dir, "transcript.txt")
        metadata_path = os.path.join(video_dir, "metadata.json")

        if not (os.path.exists(transcript_path) and os.path.exists(metadata_path)):
            return None

        try:
            # Load transcript
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()

            # Load metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Update last accessed time in global metadata
            self._update_last_accessed(video_id)

            return {
                "transcript": transcript,
                "title": metadata["title"],
                "description": metadata["description"],
                "url": metadata["url"],
                "word_count": metadata["word_count"],
            }

        except Exception as e:
            click.echo(f"Warning: Could not load cached transcript: {e}")
            return None

    def _update_last_accessed(self, video_id: str):
        """Update last accessed time for a video."""
        metadata = self._load_metadata()
        for video in metadata["videos"]:
            if video["id"] == video_id:
                video["last_accessed"] = datetime.now().isoformat()
                break
        self._save_metadata(metadata)

    def list_cached_videos(self) -> List[Tuple[str, str, str, str]]:
        """
        List all cached videos sorted by timestamp (newest first).

        Returns:
            List of tuples: (timestamp, description, url, title)
        """
        metadata = self._load_metadata()

        # Sort by timestamp (newest first)
        videos = sorted(metadata["videos"], key=lambda x: x["timestamp"], reverse=True)

        return [
            (video["timestamp"], video["description"], video["url"], video["title"])
            for video in videos
        ]

    def get_full_cached_data(self, url: str) -> Optional[Dict]:
        """Get full cached data for a video."""
        return self.get_cached_transcript(url)

    def is_cached(self, url: str) -> bool:
        """Check if a video is cached."""
        return self.get_cached_transcript(url) is not None

    def clear_cache(self):
        """Clear all cached data."""
        try:
            import shutil

            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
            self._ensure_cache_dir()
            click.echo("🗑️ Cache cleared")
        except Exception as e:
            click.echo(f"Error clearing cache: {e}")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        metadata = self._load_metadata()
        total_videos = len(metadata["videos"])

        if total_videos == 0:
            return {"total_videos": 0, "total_words": 0, "cache_size": "0 MB"}

        total_words = sum(video.get("word_count", 0) for video in metadata["videos"])

        # Calculate cache size
        cache_size = 0
        if os.path.exists(self.cache_dir):
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    try:
                        cache_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass

        cache_size_mb = cache_size / (1024 * 1024)

        return {
            "total_videos": total_videos,
            "total_words": total_words,
            "cache_size": f"{cache_size_mb:.2f} MB",
        }
