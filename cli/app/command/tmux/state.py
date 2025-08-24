"""Tmux state management commands."""

import shlex
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple

import click

from .models import ClaudeBinding, Session, State, Window
from .utils import (
    CLAUDE_MAP_FILE,  # noqa: F401 - needed for test patching
    STATE_FILE,
    clean_claude_map,
    create_session_if_needed,
    current_session_and_window,
    list_sessions,
    list_windows_all,
    new_window_get_id,
    read_claude_map,
    tmux,
    tmux_ok,
    window_id_for,
)


@click.group(name="state")
def state():
    """Manage tmux session and window state."""
    pass


@state.command()
def save():
    """Save current tmux layout and Claude bindings."""
    sessions = list_sessions()
    if not sessions:
        click.echo("No tmux sessions running", err=True)
        sys.exit(1)

    # Gather windows and compute ordinals per (session, name, path)
    win_all = list_windows_all()
    counts: Dict[Tuple[str, str, str], int] = {}
    sess_map: Dict[str, List[Window]] = {s: [] for s in sessions}
    for s, idx, name, path in win_all:
        key = (s, name, path)
        counts[key] = counts.get(key, 0) + 1
        ordinal = counts[key] - 1  # zero-based occurrence within (name,path)
        sess_map[s].append(Window(index=idx, name=name, path=path, ordinal=ordinal))

    # Current focus
    cur_s, cur_w = current_session_and_window()

    # Map Claude bindings: resolve pane -> (session, window_name, path, ordinal)
    bindings: List[ClaudeBinding] = []
    for session, pane_id, uuid in read_claude_map():
        # Ensure pane exists and fetch its window context
        try:
            out = tmux(
                "display-message",
                "-p",
                "-t",
                pane_id,
                "#{session_name}\t#{window_name}\t#{pane_current_path}\t#{window_index}",
            ).strip()
        except subprocess.CalledProcessError:
            continue

        # Handle panes with incomplete information (empty fields)
        parts = out.split("\t")
        if len(parts) != 4:
            continue
        s2, wname, path, windex_str = parts

        # Skip panes with empty/null session, window name, or path
        if not s2 or not wname or not path or not windex_str:
            continue

        try:
            windex = int(windex_str)
        except ValueError:
            continue

        if s2 != session:
            # Session was renamed or pane moved; still use actual session
            session = s2
        # Compute ordinal among windows with same (name,path) in this session up to this index
        ordinal = 0
        for w in sorted(sess_map.get(session, []), key=lambda x: x.index):
            if w.index >= windex:
                break
            if w.name == wname and w.path == path:
                ordinal += 1
        bindings.append(
            ClaudeBinding(
                session=session,
                window_name=wname,
                path=path,
                ordinal=ordinal,
                uuid=uuid,
            )
        )

    state_obj = State(
        created_at=datetime.now().isoformat(timespec="seconds"),
        sessions=[
            Session(name=s, windows=sorted(sess_map[s], key=lambda w: w.index))
            for s in sessions
        ],
        current_session=cur_s,
        current_window_index=cur_w,
        claude=bindings,
    )

    # Write state atomically
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(state_obj.to_json() + "\n")
    tmp.replace(STATE_FILE)

    # Also cleanup stale entries
    removed = clean_claude_map()
    click.echo(f"State saved to {STATE_FILE}")
    if removed:
        click.echo(f"Cleaned {removed} stale Claude mapping(s)")


@state.command()
def load():
    """Restore tmux layout and resume Claude sessions."""
    if not STATE_FILE.exists():
        click.echo(f"No saved state found at {STATE_FILE}", err=True)
        sys.exit(1)

    state_obj = State.from_json(STATE_FILE.read_text())
    click.echo("Loading tmux window state with Claude sessions...")

    # Build quick lookup for Claude bindings per session keyed by (name, path, ordinal)
    claude_map: Dict[Tuple[str, str, str, int], str] = {}
    for c in state_obj.claude:
        claude_map[(c.session, c.window_name, c.path, c.ordinal)] = c.uuid

    for sess in state_obj.sessions:
        if not sess.windows:
            continue
        # Ensure session exists (create with first window)
        first = sorted(sess.windows, key=lambda w: w.index)[0]
        create_session_if_needed(sess.name, first)

        # For existing sessions, ensure the first window has correct name/path
        # Get the actual first window index (might not be 0)
        try:
            existing_windows = (
                tmux("list-windows", "-t", sess.name, "-F", "#{window_index}")
                .strip()
                .split()
            )
            if existing_windows:
                first_index = min(int(w) for w in existing_windows)
                tmux("rename-window", "-t", f"{sess.name}:{first_index}", first.name)
                tmux(
                    "send-keys",
                    "-t",
                    f"{sess.name}:{first_index}",
                    f"cd {shlex.quote(first.path)}",
                    "Enter",
                )
        except subprocess.CalledProcessError:
            pass  # Session might not exist yet or other issue

        # Collect created/adjusted window IDs by (name, path) occurrence
        occurrence: Dict[Tuple[str, str], int] = {}

        # Process windows in ascending index order
        first_window_processed = False
        for w in sorted(sess.windows, key=lambda w: w.index):
            if not first_window_processed:
                # First window was already created/renamed above, just get its ID
                wid = window_id_for(sess.name, w.index)
                first_window_processed = True
            else:
                wid = new_window_get_id(sess.name, w.name, w.path)
            key = (w.name, w.path)
            occ = occurrence.get(key, 0)
            occurrence[key] = occ + 1

            # If Claude bound to this window, resume it targeting by window-id
            uuid = claude_map.get((sess.name, w.name, w.path, occ))
            if uuid:
                tmux(
                    "send-keys",
                    "-t",
                    wid,
                    f"claude --resume {shlex.quote(uuid)}",
                    "Enter",
                )

    # Switch to previously active session/window
    if (
        state_obj.current_session is not None
        and state_obj.current_window_index is not None
    ):
        target = f"{state_obj.current_session}:{state_obj.current_window_index}"
        if not tmux_ok("switch-client", "-t", target):
            tmux_ok("attach-session", "-t", target)
    click.echo(f"State restored from {STATE_FILE}")
