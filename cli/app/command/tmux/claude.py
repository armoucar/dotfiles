"""Claude session management commands for tmux integration."""

import os
import sys
import uuid as _uuid

import click

from .utils import CLAUDE_MAP_FILE, tmux


@click.command(name="claude-start", context_settings={"ignore_unknown_options": True})
@click.argument("claude_args", nargs=-1, type=click.UNPROCESSED)
def claude_start(claude_args):
    """Start Claude Code with UUID tracking for tmux window state management."""
    if not os.environ.get("TMUX"):
        click.echo("Error: Must be run from within a tmux session", err=True)
        sys.exit(1)

    uuid = str(_uuid.uuid4())

    try:
        session = tmux("display-message", "-p", "#{session_name}").strip()
        window = tmux("display-message", "-p", "#{window_name}").strip()
        pane_id = tmux("display-message", "-p", "#{pane_id}").strip()
    except RuntimeError as e:
        click.echo(f"Error getting tmux info: {e}", err=True)
        sys.exit(1)

    click.echo(
        f"Starting Claude in {session}:{window} (pane {pane_id}) with session ID: {uuid}"
    )

    # Remove any existing mapping for this pane and add the new one
    lines = []
    if CLAUDE_MAP_FILE.exists():
        try:
            for line in CLAUDE_MAP_FILE.read_text().splitlines():
                if not line.strip():
                    continue
                if line.startswith(f"{session}:{pane_id}:"):
                    continue
                lines.append(line)
        except (UnicodeDecodeError, IOError):
            # Handle corrupted file by starting fresh
            lines = []

    lines.append(f"{session}:{pane_id}:{uuid}")
    tmp = CLAUDE_MAP_FILE.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n")
    tmp.replace(CLAUDE_MAP_FILE)

    # Start Claude with the specific session ID and any additional arguments
    try:
        claude_cmd = ["claude", "--session-id", uuid] + list(claude_args)
        os.execvp("claude", claude_cmd)
    except FileNotFoundError:
        click.echo(
            "Error: claude command not found. Make sure Claude Code is installed.",
            err=True,
        )
        sys.exit(1)
