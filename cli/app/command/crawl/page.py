import click
import subprocess
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from firecrawl import FirecrawlApp


@click.command()
@click.argument("url")
@click.option("--format", "-f", type=click.Choice(["markdown", "html"]), default="markdown", help="Output format")
@click.option("--no-cache", is_flag=True, help="Ignore cached results and force new scrape")
def page(url: str, format: str, no_cache: bool):
    """Scrape a webpage and copy the content to clipboard."""
    try:
        cache_path = get_cache_path(url, format)

        # Check cache first unless --no-cache is specified
        if not no_cache:
            cached_result = load_from_cache(cache_path)
            if cached_result:
                click.echo("Using cached result...")
                content = wrap_content(cached_result["data"].get(format, ""), url)
                if content:
                    process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                    process.communicate(content.encode())
                    click.echo(f"Successfully loaded cached content for {url} and copied to clipboard")
                    return

        app = FirecrawlApp()

        # Configure scrape parameters
        params = {"formats": [format]}

        # Perform the scrape
        scrape_result = app.scrape_url(url, params=params)

        if not scrape_result:
            click.echo("Error: Failed to scrape the URL", err=True)
            return

        # Get the content in the requested format
        content = scrape_result.get(format, "")
        if not content:
            click.echo("Error: No content found in the response", err=True)
            return

        content = wrap_content(content, url)

        # Save to cache
        save_to_cache(cache_path, scrape_result)

        # Copy to clipboard using pbcopy
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(content.encode())

        click.echo(f"Successfully scraped {url} and copied content to clipboard")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


def wrap_content(content: str, url: str) -> str:
    return f'<documentation_content link="{url}">\n{content}\n</documentation_content>'


def get_cache_path(url: str, format: str) -> Path:
    """Generate a cache file path based on URL and format."""
    # Create cache directory if it doesn't exist
    cache_dir = Path("/tmp/firecrawl_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Create a unique filename based on URL and format
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return cache_dir / f"{url_hash}_{format}.json"


def load_from_cache(cache_path: Path) -> dict:
    """Load cached scrape result if it exists and is valid."""
    if not cache_path.exists():
        return None

    try:
        with cache_path.open("r") as f:
            data = json.load(f)
            return data
    except:
        return None


def save_to_cache(cache_path: Path, data: dict):
    """Save scrape result to cache."""
    cache_data = {"timestamp": datetime.now().isoformat(), "data": data}
    with cache_path.open("w") as f:
        json.dump(cache_data, f)


if __name__ == "__main__":
    page(standalone_mode=False)
