import click
import os
import subprocess
import shutil

from cli.app.command.notes.utils import NOTES_DIR

@click.command()
@click.argument("query", required=True)
@click.option("--content-only", "-c", is_flag=True, help="Show only the matching content lines")
def search(query: str, content_only: bool):
    """Search for text in notes and tasks.

    Uses ripgrep if available, otherwise falls back to grep.
    Shows matching files with highlighted content matches.
    """
    if not os.path.exists(NOTES_DIR):
        click.echo("Notes directory not found.")
        return

    # Check if ripgrep is available
    rg_available = shutil.which("rg") is not None

    try:
        if rg_available:
            # Using ripgrep - better performance and highlighting
            cmd = [
                "rg",
                "-i",                          # Case insensitive
                "--color=always",              # Always colorize output
                "--heading",                   # Show filenames as headings
                "--line-number",               # Show line numbers
                "--no-messages",               # Suppress error messages
            ]

            # Only show content if requested
            if content_only:
                cmd.append("--no-filename")
                cmd.append("--no-heading")

            cmd.append(query)
            cmd.append(NOTES_DIR)

            # Run ripgrep and pipe output through less if not in content-only mode
            if not content_only:
                process = subprocess.run(cmd, capture_output=False, text=True)
            else:
                process = subprocess.run(cmd, capture_output=True, text=True)
                click.echo(process.stdout)

        else:
            # Fallback to grep
            grep_args = ["-r", "-i", "--color=always"]
            if content_only:
                grep_args.append("-h")  # Don't show filenames

            cmd = ["grep"] + grep_args + [query, NOTES_DIR]
            process = subprocess.run(cmd, capture_output=True, text=True)
            click.echo(process.stdout)

        # Check if anything was found
        if (process.returncode != 0 and process.returncode != 1) or \
           (process.returncode == 1 and (not hasattr(process, 'stdout') or not process.stdout)):
            click.echo(f"No matches found for '{query}'.")

    except Exception as e:
        click.echo(f"Error searching notes: {e}")
