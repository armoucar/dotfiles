import click
import subprocess
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from firecrawl import FirecrawlApp
import urllib.parse

from cli.app.ignore_ssl import disable_ssl_verification


@click.command()
@click.argument("url")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "html"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Ignore cached results and force new scrape",
)
@click.option("--ignore-ssl", is_flag=True, help="Ignore SSL certificate verification")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: generated from URL)",
)
def page(url: str, format: str, no_cache: bool, ignore_ssl: bool, output: str):
    """Scrape a webpage and save the content to a markdown file."""

    if ignore_ssl:
        disable_ssl_verification()

    try:
        cache_path = get_cache_path(url, format)

        # Check cache first unless --no-cache is specified
        if not no_cache:
            cached_result = load_from_cache(cache_path)
            if cached_result:
                click.echo("Using cached result...")
                content = cached_result["data"].get(format, "")
                if content:
                    output_path = get_output_path(url, output, format)
                    save_content_to_file(content, output_path)
                    click.echo(
                        f"Successfully loaded cached content for {url} and saved to {output_path}"
                    )
                    return

        app = FirecrawlApp()

        # Perform the scrape
        scrape_result = app.scrape_url(url, formats=[format])

        if not scrape_result:
            click.echo("Error: Failed to scrape the URL", err=True)
            return

        # Get the content in the requested format
        content = scrape_result.markdown if format == "markdown" else scrape_result.html
        if not content:
            click.echo("Error: No content found in the response", err=True)
            return

        # Save to cache
        save_to_cache(cache_path, content)

        # Save content to file
        output_path = get_output_path(url, output, format)
        save_content_to_file(content, output_path)

        click.echo(f"Successfully scraped {url} and saved content to {output_path}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


def get_output_path(url: str, output: str, format: str) -> Path:
    """Generate output file path based on URL and format."""
    if output:
        return Path(output)

    # Generate filename from URL
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc.replace("www.", "")
    path_parts = [part for part in parsed_url.path.split("/") if part]

    if path_parts:
        filename = f"{domain}_{'-'.join(path_parts)}"
    else:
        filename = domain

    # Clean filename and add extension
    filename = "".join(c for c in filename if c.isalnum() or c in ("-", "_")).rstrip()
    extension = "md" if format == "markdown" else "html"

    return Path(f"{filename}.{extension}")


def save_content_to_file(content: str, output_path: Path):
    """Save content to the specified file."""
    with output_path.open("w", encoding="utf-8") as f:
        f.write(content)


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
