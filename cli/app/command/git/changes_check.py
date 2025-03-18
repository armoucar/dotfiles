import click
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Dict, Any
import sys
import time
import os


def _is_interactive_terminal():
    """Check if we're in an interactive terminal."""
    return sys.stdout.isatty()


@click.command(name="changes-check")
@click.option(
    "--sort",
    type=click.Choice(["time", "edits", "changes"]),
    default="time",
    help="Sort by last modified time (default), number of edits, or list of changes by time",
)
@click.option(
    "--limit",
    type=int,
    default=20,
    help="Number of files to show per page (default: 20)",
)
@click.option(
    "--ext",
    type=str,
    help="File extension to filter (optional)",
)
@click.option(
    "--no-pager",
    is_flag=True,
    help="Disable pagination and show all results at once",
)
def changes_check(sort: str, limit: int, ext: str | None, no_pager: bool):
    """List recently modified or frequently edited files in the git repository.

    Examples:
        # List 100 most recently modified .ipynb files
        changes-check --ext ipynb

        # List 100 most frequently edited .py files
        changes-check --sort edits --ext py

        # List 100 most recently modified files (any extension)
        changes-check

        # List 100 most recent changes across all files
        changes-check --sort changes

        # List 100 most recent changes in .py files with pagination
        changes-check --sort changes --ext py

        # List all changes without pagination
        changes-check --sort changes --no-pager
    """

    # Force no-pager mode if we're not in an interactive terminal
    if not _is_interactive_terminal():
        no_pager = True

    # For changes mode, we handle differently
    if sort == "changes":
        _handle_changes_mode(limit, ext, no_pager)
        return

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

        # Format output
        start_time = time.time()
        formatter = _get_formatted_timestamp if sort == "time" else _get_formatted_count

        # Handle pagination
        if no_pager:
            formatted_output = _process_files_in_parallel(executor, formatter, file_data, len(file_data))
            formatting_time = time.time() - start_time
            click.echo(f"\nFormatting output took {formatting_time:.2f} seconds")

            # Display all results with counter
            total_results = len(formatted_output)
            click.secho(f"\nFound {total_results} results:", fg="blue")
            for i, output in enumerate(formatted_output, 1):
                click.echo(f"{i:4d}. {output}")
        else:
            # Paginate through results
            _paginate_results(file_data, executor, formatter, limit)


def _handle_changes_mode(limit: int, ext: str | None, no_pager: bool):
    """Handle the changes mode to display a list of changes sorted by time."""
    # Get current directory relative to git repo
    try:
        current_dir = os.getcwd()
        repo_root = _run_git_command(["git", "rev-parse", "--show-toplevel"])

        # Convert current_dir to be relative to repo root if it's under the repo
        if current_dir.startswith(repo_root):
            relative_dir = os.path.relpath(current_dir, repo_root)
            if relative_dir == ".":
                relative_dir = ""  # Root directory case
            click.secho(f"Listing changes in directory: ", nl=False, fg="bright_blue")
            click.secho(f"{relative_dir or '/'}", fg="white")
        else:
            click.secho("Current directory is not inside the git repository", fg="red")
            return

        click.secho("Loading commits... (this may take a few moments)", fg="cyan")
        start_time = time.time()

        # Collect all changes with lazy loading
        changes_collector = _ChangesCollector(relative_dir, ext, limit)

        # Get initial batch of changes
        changes = changes_collector.get_next_batch()

        if not changes:
            click.secho("No changes found matching criteria", fg="yellow")
            return

        processing_time = time.time() - start_time

        # Show different messages depending on paging mode
        if no_pager:
            click.secho("Loading all changes...", fg="cyan")
            # Just load and display all changes
            all_changes = changes
            while changes_collector.has_more():
                more_changes = changes_collector.get_next_batch()
                if not more_changes:
                    break
                all_changes.extend(more_changes)

            total_processing_time = time.time() - start_time
            click.secho(f"Found ", nl=False, fg="bright_blue")
            click.secho(f"{len(all_changes)}", nl=False, fg="bright_white", bold=True)
            click.secho(f" changes (loaded in {total_processing_time:.2f} seconds)", fg="bright_blue")

            # Add a separator line
            click.secho("─" * 80, fg="bright_blue")

            # Display all changes with counter
            for i, (timestamp, change_type, file_path, author) in enumerate(all_changes, 1):
                _print_change_entry(i, timestamp, change_type, file_path, author)
        else:
            click.secho(f"Initial batch loaded in {processing_time:.2f} seconds. Starting pagination...", fg="cyan")
            # Use pagination for changes
            _paginate_changes(changes_collector)

    except subprocess.CalledProcessError as e:
        click.secho(f"Error executing git command: {e}", fg="red")
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg="red")


def _paginate_results(file_data: List, executor: ThreadPoolExecutor, formatter, page_size: int):
    """Paginate through results with dynamic loading."""
    current_page = 1
    total_items = len(file_data)
    total_pages = (total_items + page_size - 1) // page_size

    # Function to display a page of results
    def display_page(page_num):
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)

        # Get items for current page
        page_items = file_data[start_idx:end_idx]

        # Format the items for this page
        formatted_items = _process_files_in_parallel(executor, formatter, page_items, len(page_items))

        # Clear screen and show current page
        click.clear()
        click.secho(
            f"Page {page_num}/{total_pages} - Showing items {start_idx+1}-{end_idx} of {total_items}", fg="blue"
        )
        click.secho("Navigation: [n]ext page | [p]revious page | [q]uit", fg="cyan")
        print()  # Add a blank line for readability

        # Display the page
        for i, item in enumerate(formatted_items, start_idx + 1):
            click.echo(f"{i:4d}. {item}")

        print()  # Add a blank line after content
        click.secho("Command: ", nl=False, fg="green")

    # Initial page display
    display_page(current_page)

    # Handle pagination input
    while True:
        key = click.getchar().lower()

        if key == "n":  # next page
            if current_page < total_pages:
                current_page += 1
                display_page(current_page)
            else:
                click.clear()
                display_page(current_page)
                click.secho("You've reached the last page.", fg="yellow")
                click.secho("Command: ", nl=False, fg="green")
        elif key == "p":  # previous page
            if current_page > 1:
                current_page -= 1
                display_page(current_page)
            else:
                click.clear()
                display_page(current_page)
                click.secho("You're already on the first page.", fg="yellow")
                click.secho("Command: ", nl=False, fg="green")
        elif key == "q":  # quit
            break
        else:
            # Redraw current page if invalid key
            click.clear()
            display_page(current_page)
            click.secho(f"Unknown command: '{key}'. Use n, p, or q.", fg="yellow")
            click.secho("Command: ", nl=False, fg="green")


class _ChangesCollector:
    """Collect changes with lazy loading capabilities."""

    def __init__(self, relative_dir: str, ext: str | None, batch_size: int):
        self.relative_dir = relative_dir
        self.ext = ext
        self.batch_size = batch_size
        self.current_batch = 0
        self.commits_loaded = 0
        self.last_commit = None
        self.all_changes = []
        self.has_more_commits = True
        # Cache for batches we've already seen
        self.batch_cache = {}

    def has_more(self):
        """Check if there are potentially more changes to load."""
        # If we have stored changes beyond current batch, or there are more commits to check
        return self.has_more_commits or len(self.all_changes) > self.current_batch * self.batch_size

    def get_next_batch(self):
        """Get the next batch of changes."""
        start_idx = self.current_batch * self.batch_size

        # Check if this batch is already in the cache
        if self.current_batch in self.batch_cache:
            self.current_batch += 1
            return self.batch_cache[self.current_batch - 1]

        # If we don't have enough changes, try to load more
        while self.has_more_commits and len(self.all_changes) < start_idx + self.batch_size:
            self._load_more_commits()

        # If we still don't have enough changes for a complete batch but no more commits
        if start_idx >= len(self.all_changes):
            return []

        # Get the next batch
        end_idx = min(start_idx + self.batch_size, len(self.all_changes))
        batch = self.all_changes[start_idx:end_idx]

        # Cache this batch
        self.batch_cache[self.current_batch] = batch
        self.current_batch += 1

        return batch

    def get_batch_at_page(self, page: int):
        """Get a specific batch by page number (0-indexed)."""
        # Check if this batch is already in the cache
        if page in self.batch_cache:
            return self.batch_cache[page]

        # If we're requesting a page we haven't loaded yet
        current_page = self.current_batch

        # Reset to the requested page
        self.current_batch = page

        # Get the batch
        batch = self.get_next_batch()

        # Restore the current page (minus 1 because get_next_batch increments it)
        self.current_batch = current_page

        return batch

    def _load_more_commits(self):
        """Load more commits to get changes."""
        # Determine how many commits to fetch
        commits_to_fetch = self.batch_size * 5  # Fetch more commits as we'll filter them

        # Build git command to get commits
        git_log_cmd = ["git", "log", "--pretty=format:%H", f"-n", f"{commits_to_fetch}"]

        # Add pagination using --skip
        if self.commits_loaded > 0:
            git_log_cmd.extend(["--skip", f"{self.commits_loaded}"])

        # Add path filtering if needed
        if self.relative_dir:
            git_log_cmd.extend(["--", f"{self.relative_dir}"])
        elif self.ext:
            git_log_cmd.extend(["--", f"*.{self.ext}"])

        # Run the command
        commits_output = _run_git_command(git_log_cmd)
        if not commits_output:
            self.has_more_commits = False
            return

        commits = commits_output.split("\n")
        if not commits or commits[0] == "":
            self.has_more_commits = False
            return

        # Process each commit to get changed files
        for commit in commits:
            if not commit:
                continue

            # Get commit timestamp and author
            commit_info = _run_git_command(
                ["git", "show", "-s", "--format=%cd|%an", "--date=format:[%Y-%m-%d %H:%M:%S]", commit]
            ).split("|")

            if len(commit_info) < 2:
                continue

            timestamp, author = commit_info[0], commit_info[1]

            # Get file changes with status (A/M/D)
            file_changes_cmd = ["git", "show", "--name-status", "--format=", commit]
            file_changes = _run_git_command(file_changes_cmd).split("\n")

            # Process each file change
            for change in file_changes:
                if not change.strip():
                    continue

                parts = change.strip().split("\t")
                if len(parts) < 2:
                    continue

                change_type = parts[0][0]  # Get first character (A/M/D/R/C)
                file_path = parts[-1]  # Last part is the file name (in case of renames)

                # Skip files not in the current directory
                if self.relative_dir:
                    if not (
                        file_path == self.relative_dir
                        or file_path.startswith(f"{self.relative_dir}/")
                        or (self.relative_dir == "" and "/" not in file_path)
                    ):
                        continue

                # Apply extension filter if needed
                if self.ext and not file_path.endswith(f".{self.ext}"):
                    continue

                # Simplify change type
                if change_type in "RC":  # Rename or Copy
                    change_type = "A"  # Treat as Added

                # Add to changes list with change type and author
                self.all_changes.append((timestamp, change_type, file_path, author))

        self.commits_loaded += len(commits)
        self.last_commit = commits[-1] if commits else None

        # Check if we've reached the end
        if len(commits) < commits_to_fetch:
            self.has_more_commits = False


def _paginate_changes(changes_collector: _ChangesCollector):
    """Display changes with pagination."""
    # Track which page we're viewing
    page = 0
    total_viewed = 0
    total_changes = 0
    first_page = True
    # Keep track of pages we've already seen
    viewed_pages = set()

    while True:
        # Clear screen for better UI (except first time)
        if not first_page:
            # Use ANSI escape sequence to clear screen
            click.echo("\033c", nl=False)
        else:
            first_page = False

        # Get batch for the current page
        start_time = time.time()

        # Check if we've already viewed this page
        if page in viewed_pages:
            current_batch = changes_collector.get_batch_at_page(page)
            load_time = time.time() - start_time
            if load_time < 0.01:  # If loading was very fast
                load_message = "(cached)"
            else:
                load_message = f"(loaded in {load_time:.2f}s)"
        else:
            # First time viewing this page
            if page < changes_collector.current_batch:
                # We're going back to a page we should have cached
                current_batch = changes_collector.get_batch_at_page(page)
                load_message = "(cached)"
            else:
                # Loading a new page
                current_batch = changes_collector.get_next_batch()
                load_message = f"(loaded in {time.time() - start_time:.2f}s)"
            viewed_pages.add(page)

        if not current_batch:
            click.secho("No more changes to display.", fg="yellow")
            return

        # Keep track of how many we've seen
        batch_size = len(current_batch)
        has_more = changes_collector.has_more()

        # Calculate range for display
        start_idx = page * changes_collector.batch_size + 1
        end_idx = start_idx + batch_size - 1

        # Increment total viewed and update total changes if we know it
        if page >= len(viewed_pages) - 1:  # Only count if this is a new page
            total_viewed += batch_size
        if not has_more:
            total_changes = total_viewed

        # Show header with range
        range_info = f"Showing changes {start_idx}-{end_idx}"
        if total_changes > 0:
            range_info += f" of {total_changes}"
        range_info += f" {load_message}"

        click.secho(range_info, fg="bright_blue", bold=True)
        click.secho("─" * len(range_info), fg="bright_blue")

        # Display changes
        for i, (timestamp, change_type, file_path, author) in enumerate(current_batch, start_idx):
            _print_change_entry(i, timestamp, change_type, file_path, author)

        # Show navigation instructions
        click.secho("\nNavigation:", fg="bright_cyan", bold=True)
        if page > 0:
            click.secho("  p", nl=False, fg="bright_green")
            click.secho(" - previous page", fg="white")
        if has_more:
            click.secho("  n", nl=False, fg="bright_green")
            click.secho(" - next page", fg="white")
        click.secho("  q", nl=False, fg="bright_green")
        click.secho(" - quit", fg="white")

        # Get user input for navigation
        click.secho("\nCommand: ", nl=False, fg="bright_green")
        while True:
            key = click.getchar()
            if key == "n" and has_more:
                page += 1
                break
            elif key == "p" and page > 0:
                page -= 1
                break
            elif key == "q":
                return
            else:
                # Clear the line and show error for invalid key
                click.echo("\r" + " " * 50, nl=False)  # Clear the line
                click.echo("\r", nl=False)
                click.secho("Invalid command. ", nl=False, fg="red")
                click.secho("Command: ", nl=False, fg="bright_green")


def _print_change_entry(index: int, timestamp: str, change_type: str, file_path: str, author: str):
    """Print a change entry with appropriate colors."""
    # Color the index and timestamp in blue
    click.secho(f"{index:4d}. ", nl=False, fg="blue")
    click.secho(f"{timestamp} ", nl=False, fg="cyan")

    # Color the change type based on the operation
    if change_type == "A":
        click.secho(f"{change_type} ", nl=False, fg="green")  # Added - green
    elif change_type == "M":
        click.secho(f"{change_type} ", nl=False, fg="yellow")  # Modified - yellow
    elif change_type == "D":
        click.secho(f"{change_type} ", nl=False, fg="red")  # Deleted - red
    else:
        click.secho(f"{change_type} ", nl=False, fg="magenta")  # Other changes - magenta

    # Use consistent color for file paths (bright_blue)
    click.secho(f"{file_path} ", nl=False, fg="bright_blue")

    # Color the author name in a subtle gray
    click.secho(f"({author})", fg="bright_black")


def _run_git_command(args: List[str]) -> str:
    """Run a git command and return stripped output."""
    try:
        return subprocess.check_output(args, stderr=subprocess.PIPE).decode().strip()
    except subprocess.CalledProcessError as e:
        # Return empty string on error
        return ""


def _show_progress(msg: str, current: int, total: int) -> None:
    """Show progress bar."""
    sys.stdout.write(f"\r{msg}: {current}/{total}")
    sys.stdout.flush()


def _get_commit_timestamp(args: Tuple[str, int, int]) -> Tuple[int, str]:
    """Get the Unix timestamp of last commit for a file."""
    file, current, total = args
    _show_progress("Processing files", current, total)
    last_commit_epoch = int(_run_git_command(["git", "log", "-1", "--format=%ct", file]) or "0")
    return (last_commit_epoch, file)


def _get_commit_count(args: Tuple[str, int, int]) -> Tuple[int, str]:
    """Get the number of commits that touched a file."""
    file, current, total = args
    _show_progress("Processing files", current, total)
    commit_count = int(_run_git_command(["git", "rev-list", "--count", "HEAD", file]) or "0")
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
    if not items:
        return []
    return list(executor.map(func, [(item, i + 1, total) for i, item in enumerate(items)]))
