"""Claude session management commands for tmux integration."""

import os
import sys
import uuid as _uuid
from pathlib import Path
import json
from datetime import datetime

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


@click.command(name="claude-resume")
@click.argument("session_id", required=False)
def claude_resume(session_id):
    """Resume a Claude session with interactive selection or direct session ID."""
    if not os.environ.get("TMUX"):
        click.echo("Error: Must be run from within a tmux session", err=True)
        sys.exit(1)

    claude_projects_dir = Path.home() / ".claude" / "projects"

    if not claude_projects_dir.exists():
        click.echo("Error: No Claude projects directory found", err=True)
        sys.exit(1)

    # If session ID provided directly, use it
    if session_id:
        try:
            session = tmux("display-message", "-p", "#{session_name}").strip()
            window = tmux("display-message", "-p", "#{window_name}").strip()
            pane_id = tmux("display-message", "-p", "#{pane_id}").strip()
        except RuntimeError as e:
            click.echo(f"Error getting tmux info: {e}", err=True)
            sys.exit(1)

        click.echo(
            f"Resuming Claude session {session_id} in {session}:{window} (pane {pane_id})"
        )

        # Update mapping for this pane
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
                lines = []

        lines.append(f"{session}:{pane_id}:{session_id}")
        tmp = CLAUDE_MAP_FILE.with_suffix(".tmp")
        tmp.write_text("\n".join(lines) + "\n")
        tmp.replace(CLAUDE_MAP_FILE)

        # Resume Claude with the session ID
        try:
            claude_cmd = ["claude", "--resume", session_id]
            os.execvp("claude", claude_cmd)
        except FileNotFoundError:
            click.echo(
                "Error: claude command not found. Make sure Claude Code is installed.",
                err=True,
            )
            sys.exit(1)
        return

    # Interactive session selection
    session_files = []
    for project_dir in claude_projects_dir.iterdir():
        if project_dir.is_dir():
            for session_file in project_dir.glob("*.jsonl"):
                if session_file.stat().st_size > 0:  # Only non-empty sessions
                    session_files.append(session_file)

    if not session_files:
        click.echo("No Claude sessions found to resume", err=True)
        sys.exit(1)

    # Sort by modification time (most recent first)
    session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    # Get session info for display
    sessions_info = []
    for session_file in session_files[:10]:  # Show only last 10 sessions
        try:
            # Read first line to get basic info
            first_line = session_file.read_text().split("\n")[0]
            data = json.loads(first_line)

            # Get session ID from filename
            session_id_from_file = session_file.stem

            # Get modification time
            mod_time = datetime.fromtimestamp(session_file.stat().st_mtime)

            # Try to get first user message for preview
            preview = "No message"
            for line in session_file.read_text().split("\n"):
                if not line.strip():
                    continue
                try:
                    line_data = json.loads(line)
                    if line_data.get("type") == "user" and "message" in line_data:
                        content = line_data["message"].get("content", "")
                        if isinstance(content, str) and content.strip():
                            preview = content[:50] + (
                                "..." if len(content) > 50 else ""
                            )
                            break
                        elif isinstance(content, list) and len(content) > 0:
                            text_content = next(
                                (
                                    c.get("text", "")
                                    for c in content
                                    if c.get("type") == "text"
                                ),
                                "",
                            )
                            if text_content:
                                preview = text_content[:50] + (
                                    "..." if len(text_content) > 50 else ""
                                )
                                break
                except (json.JSONDecodeError, KeyError):
                    continue

            sessions_info.append(
                {
                    "id": session_id_from_file,
                    "time": mod_time,
                    "preview": preview,
                    "file": session_file,
                }
            )
        except (json.JSONDecodeError, IOError, IndexError):
            continue

    if not sessions_info:
        click.echo("No valid Claude sessions found to resume", err=True)
        sys.exit(1)

    # Display sessions for selection
    click.echo("\nRecent Claude sessions:")
    click.echo("=" * 60)

    choices = []
    for i, info in enumerate(sessions_info):
        display_id = info["id"][:8] + "..." if len(info["id"]) > 12 else info["id"]
        time_str = info["time"].strftime("%Y-%m-%d %H:%M")
        click.echo(f"{i + 1:2d}. {time_str} | {display_id} | {info['preview']}")
        choices.append(str(i + 1))

    click.echo()

    # Get user selection
    try:
        selection = click.prompt(
            "Select session to resume", type=click.Choice(choices), show_choices=False
        )
        selected_session = sessions_info[int(selection) - 1]

        # Now resume with the selected session
        try:
            session = tmux("display-message", "-p", "#{session_name}").strip()
            window = tmux("display-message", "-p", "#{window_name}").strip()
            pane_id = tmux("display-message", "-p", "#{pane_id}").strip()
        except RuntimeError as e:
            click.echo(f"Error getting tmux info: {e}", err=True)
            sys.exit(1)

        click.echo(
            f"Resuming Claude session {selected_session['id']} in {session}:{window} (pane {pane_id})"
        )

        # Update mapping for this pane
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
                lines = []

        lines.append(f"{session}:{pane_id}:{selected_session['id']}")
        tmp = CLAUDE_MAP_FILE.with_suffix(".tmp")
        tmp.write_text("\n".join(lines) + "\n")
        tmp.replace(CLAUDE_MAP_FILE)

        # Resume Claude with the session ID
        try:
            claude_cmd = ["claude", "--resume", selected_session["id"]]
            os.execvp("claude", claude_cmd)
        except FileNotFoundError:
            click.echo(
                "Error: claude command not found. Make sure Claude Code is installed.",
                err=True,
            )
            sys.exit(1)

    except click.Abort:
        click.echo("Resume cancelled.")
        sys.exit(0)
