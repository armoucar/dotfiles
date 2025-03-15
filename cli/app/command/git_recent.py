import click
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List
import sys
import time


@click.command()
@click.option(
    "--sort",
    type=click.Choice(["time", "edits"]),
    default="time",
    help="Sort by last modified time (default) or number of edits",
)
@click.option(
    "--limit",
    type=int,
    default=50,
    help="Number of files to show (default: 50)",
)
@click.option(
    "--ext",
    type=str,
    help="File extension to filter (optional)",
)
def git_recent(sort: str, limit: int, ext: str | None):
    """List recently modified or frequently edited files in the git repository.

    Examples:
        # List 50 most recently modified .ipynb files
        git-recent --ext ipynb

        # List 20 most frequently edited .py files
        git-recent --sort edits --limit 20 --ext py

        # List 50 most recently modified files (any extension)
        git-recent
    """

    # Get list of files with specified extension
    if ext:
        click.secho(f"Listing files with extension: {ext}", fg="blue")
        files = _run_git_command(["git", "ls-files", f"*.{ext}"]).split("\n")
    else:
        click.secho("Listing all files", fg="blue")
        files = _run_git_command(["git", "ls-files"]).split("\n")
    total_files = len(files)
    click.secho(f"Found {total_files} total files", fg="blue")
    if total_files == 0:
        click.secho("No files found matching criteria", fg="yellow")
        return

    # Process files and format output
    with ThreadPoolExecutor() as executor:
        # Get and sort file data
        start_time = time.time()
        file_data = _process_files_in_parallel(
            executor, _get_commit_timestamp if sort == "time" else _get_commit_count, files, total_files
        )
        processing_time = time.time() - start_time
        click.echo(f"\nProcessing files took {processing_time:.2f} seconds")

        file_data.sort(reverse=True)
        file_data = file_data[:limit]  # Take top N based on limit parameter

        # Format output
        start_time = time.time()
        formatter = _get_formatted_timestamp if sort == "time" else _get_formatted_count
        formatted_output = _process_files_in_parallel(executor, formatter, file_data, len(file_data))
        formatting_time = time.time() - start_time
        click.echo(f"\nFormatting output took {formatting_time:.2f} seconds")

    for output in formatted_output:
        click.echo(output)


def _run_git_command(args: List[str]) -> str:
    """Run a git command and return stripped output."""
    return subprocess.check_output(args).decode().strip()


def _show_progress(msg: str, current: int, total: int) -> None:
    """Show progress bar."""
    sys.stdout.write(f"\r{msg}: {current}/{total}")
    sys.stdout.flush()


def _get_commit_timestamp(args: Tuple[str, int, int]) -> Tuple[int, str]:
    """Get the Unix timestamp of last commit for a file."""
    file, current, total = args
    _show_progress("Processing files", current, total)
    last_commit_epoch = int(_run_git_command(["git", "log", "-1", "--format=%ct", file]))
    return (last_commit_epoch, file)


def _get_commit_count(args: Tuple[str, int, int]) -> Tuple[int, str]:
    """Get the number of commits that touched a file."""
    file, current, total = args
    _show_progress("Processing files", current, total)
    commit_count = int(_run_git_command(["git", "rev-list", "--count", "HEAD", file]))
    return (commit_count, file)


def _get_formatted_timestamp(args: Tuple[Tuple[int, str], int, int]) -> str:
    """Get formatted timestamp string for a file."""
    epoch_and_file, current, total = args
    _, file = epoch_and_file
    _show_progress("Formatting timestamps", current, total)
    timestamp = _run_git_command(["git", "log", "-1", "--format=%cd", "--date=format:[%Y-%m-%d %H:%M:%S]", file])
    return f"{timestamp}: {file}"


def _get_formatted_count(args: Tuple[Tuple[int, str], int, int]) -> str:
    """Get formatted commit count string for a file."""
    count_and_file, current, total = args
    count, file = count_and_file
    _show_progress("Formatting output", current, total)
    return f"[{count} commits]: {file}"


def _process_files_in_parallel(executor: ThreadPoolExecutor, func, items, total: int):
    """Process files in parallel using the given function."""
    return list(executor.map(func, [(item, i + 1, total) for i, item in enumerate(items)]))
