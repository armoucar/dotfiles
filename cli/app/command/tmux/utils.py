"""Utilities for tmux operations."""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

# Default file locations
STATE_FILE = Path.home() / ".tmux-window-state.json"
CLAUDE_MAP_FILE = Path.home() / ".tmux-claude-map"


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the completed process."""
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check
    )


def tmux(*args: str, check: bool = True) -> str:
    """Run a tmux command and return stdout."""
    cp = run(["tmux", *args], check=check)
    return cp.stdout


def tmux_ok(*args: str) -> bool:
    """Run a tmux command and return True if successful."""
    try:
        run(["tmux", *args])
        return True
    except subprocess.CalledProcessError:
        return False


def list_sessions() -> List[str]:
    """List all tmux session names."""
    try:
        out = tmux("list-sessions", "-F", "#{session_name}")
    except subprocess.CalledProcessError:
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]


def list_windows_all() -> List[Tuple[str, int, str, str]]:
    """List all windows across all sessions.

    Returns: List of (session, index, name, path) tuples
    """
    fmt = "#{session_name}\t#{window_index}\t#{window_name}\t#{pane_current_path}"
    out = tmux("list-windows", "-a", "-F", fmt)
    res = []
    for line in out.splitlines():
        if not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) != 4:
            continue  # Skip malformed lines

        s, idx_str, name, path = parts
        try:
            idx = int(idx_str)
        except ValueError:
            continue  # Skip lines with non-numeric window index

        res.append((s, idx, name, path))
    return res


def current_session_and_window() -> Tuple[Optional[str], Optional[int]]:
    """Get current session name and window index."""
    try:
        out = tmux("display-message", "-p", "#{session_name}\t#{window_index}")
        s, w = out.strip().split("\t", 1)
        return s, int(w)
    except Exception:
        return None, None


def read_claude_map() -> List[Tuple[str, str, str]]:
    """Read Claude session mappings.

    Returns: List of (session, pane_id, uuid) tuples
    """
    if not CLAUDE_MAP_FILE.exists():
        return []

    try:
        content = CLAUDE_MAP_FILE.read_text()
    except UnicodeDecodeError:
        return []  # Handle corrupted files gracefully

    entries = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.rsplit(":", 2)
        if len(parts) != 3:
            continue
        session, pane_id, uuid = parts
        # Skip entries with empty fields
        if not session or not pane_id or not uuid:
            continue
        entries.append((session, pane_id, uuid))
    return entries


def clean_claude_map() -> int:
    """Clean stale entries from Claude map file.

    Returns: Number of entries removed
    """
    entries = read_claude_map()
    kept: List[str] = []
    removed = 0
    # Build a set of existing panes: "session:pane_id"
    try:
        existing = set(
            l.strip()
            for l in tmux(
                "list-panes", "-a", "-F", "#{session_name}:#{pane_id}"
            ).splitlines()
            if l.strip()
        )
    except subprocess.CalledProcessError:
        existing = set()

    for session, pane_id, uuid in entries:
        key = f"{session}:{pane_id}"
        if key in existing:
            kept.append(f"{session}:{pane_id}:{uuid}")
        else:
            removed += 1

    # Atomic write
    tmp = CLAUDE_MAP_FILE.with_suffix(".tmp")
    tmp.write_text("\n".join(kept) + ("\n" if kept else ""))
    tmp.replace(CLAUDE_MAP_FILE)
    return removed


def create_session_if_needed(name: str, first_win) -> None:
    """Create tmux session if it doesn't exist."""
    # If session exists, do nothing
    if tmux_ok("has-session", "-t", name):
        return
    # Create with the first window name/path
    tmux(
        "new-session",
        "-d",
        "-s",
        name,
        "-n",
        first_win.name,
        "-c",
        first_win.path,
        "-P",
        "-F",
        "#{window_id}",
    )


def window_id_for(session: str, index: int) -> Optional[str]:
    """Get window ID for a specific session and window index."""
    try:
        out = tmux("list-windows", "-t", session, "-F", "#{window_index}\t#{window_id}")
    except subprocess.CalledProcessError:
        return None
    for line in out.splitlines():
        i_str, wid = line.split("\t", 1)
        if int(i_str) == index:
            return wid.strip()
    return None


def new_window_get_id(session: str, name: str, path: str) -> str:
    """Create a new window and return its ID."""
    out = tmux(
        "new-window",
        "-t",
        session,
        "-n",
        name,
        "-c",
        path,
        "-P",
        "-F",
        "#{window_id}",
    )
    return out.strip()
