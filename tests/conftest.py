"""Shared fixtures and configuration for tmux-claude state management tests."""

import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Dict, List
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_home(tmp_path):
    """Create a temporary home directory for testing."""
    return tmp_path


@pytest.fixture
def sample_state_json():
    """Load sample state JSON for testing."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_state.json"
    return json.loads(fixture_path.read_text())


@pytest.fixture
def sample_claude_map_content():
    """Load sample Claude map content for testing."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_claude_map"
    return fixture_path.read_text()


@pytest.fixture
def mock_tmux_responses():
    """Mock tmux command responses."""
    return {
        "list-sessions": "main-session\ntesting\n",
        "list-windows-all": "main-session\t1\teditor\t/home/user/project\nmain-session\t2\tterminal\t/home/user/project\nmain-session\t3\teditor\t/home/user/docs\ntesting\t1\ttest-runner\t/home/user/project/tests\n",
        "current-session-window": "main-session\t2\n",
        "display-message-pane": "main-session\teditor\t/home/user/project\t1\n",
        "list-panes-all": "main-session:%1\nmain-session:%2\nmain-session:%3\ntesting:%4\n",
        "list-windows-session": "1\t2\t3\n",
        "has-session": "",
        "new-session": "@1\n",
        "new-window": "@4\n",
        "list-windows-with-ids": "1\t@1\n2\t@2\n3\t@3\n",
    }


@pytest.fixture
def mock_subprocess_run(mocker, mock_tmux_responses):
    """Mock subprocess.run for tmux commands."""

    def mock_run(cmd, **kwargs):
        if cmd[0] != "tmux":
            # Let non-tmux commands through
            return CompletedProcess(cmd, 0, "", "")

        # Handle tmux commands
        if "list-sessions" in cmd:
            return CompletedProcess(cmd, 0, mock_tmux_responses["list-sessions"], "")
        elif "list-windows" in cmd and "-a" in cmd:
            format_str = next((arg for arg in cmd if "#{session_name}" in arg), None)
            if format_str:
                return CompletedProcess(
                    cmd, 0, mock_tmux_responses["list-windows-all"], ""
                )
        elif "display-message" in cmd and "#{session_name}" in " ".join(cmd):
            if "#{window_index}" in " ".join(cmd):
                return CompletedProcess(
                    cmd, 0, mock_tmux_responses["current-session-window"], ""
                )
            elif "#{window_name}" in " ".join(cmd):
                return CompletedProcess(
                    cmd, 0, mock_tmux_responses["display-message-pane"], ""
                )
        elif "list-panes" in cmd and "-a" in cmd:
            return CompletedProcess(cmd, 0, mock_tmux_responses["list-panes-all"], "")
        elif "list-windows" in cmd and "-t" in cmd:
            return CompletedProcess(
                cmd, 0, mock_tmux_responses["list-windows-session"], ""
            )
        elif "has-session" in cmd:
            return CompletedProcess(cmd, 0, mock_tmux_responses["has-session"], "")
        elif "new-session" in cmd:
            return CompletedProcess(cmd, 0, mock_tmux_responses["new-session"], "")
        elif "new-window" in cmd:
            return CompletedProcess(cmd, 0, mock_tmux_responses["new-window"], "")
        elif "list-windows" in cmd and "#{window_id}" in " ".join(cmd):
            return CompletedProcess(
                cmd, 0, mock_tmux_responses["list-windows-with-ids"], ""
            )
        else:
            # Default success for other tmux commands
            return CompletedProcess(cmd, 0, "", "")

    return mocker.patch("subprocess.run", side_effect=mock_run)


@pytest.fixture
def mock_uuid4(mocker):
    """Mock uuid4 to return predictable UUIDs."""
    mock_uuid = Mock()
    mock_uuid.__str__ = Mock(return_value="550e8400-e29b-41d4-a716-446655440000")
    return mocker.patch("uuid.uuid4", return_value=mock_uuid)


@pytest.fixture
def mock_datetime_now():
    """Mock datetime.now for predictable timestamps by patching script_globals directly."""
    # Import script_globals from the test module
    from tests.test_tmux_window_state import script_globals

    mock_datetime = Mock()
    mock_datetime.isoformat.return_value = "2025-08-24T12:00:00"

    # Create a mock datetime class with a now method
    mock_datetime_class = Mock()
    mock_datetime_class.now.return_value = mock_datetime

    original = script_globals.get("datetime")
    script_globals["datetime"] = mock_datetime_class

    yield mock_datetime_class

    # Restore original
    if original:
        script_globals["datetime"] = original


@pytest.fixture
def mock_os_environ(mocker):
    """Mock os.environ with TMUX set."""
    return mocker.patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"})


class TmuxCommandBuilder:
    """Helper class to build complex tmux command responses."""

    @staticmethod
    def list_windows_format(sessions_data: Dict[str, List[Dict]]) -> str:
        """Build list-windows -a output from structured data."""
        lines = []
        for session_name, windows in sessions_data.items():
            for window in windows:
                line = f"{session_name}\t{window['index']}\t{window['name']}\t{window['path']}"
                lines.append(line)
        return "\n".join(lines) + "\n"

    @staticmethod
    def list_panes_format(pane_data: List[Dict]) -> str:
        """Build list-panes -a output from structured data."""
        lines = []
        for pane in pane_data:
            line = f"{pane['session']}:{pane['pane_id']}"
            lines.append(line)
        return "\n".join(lines) + "\n"


@pytest.fixture
def tmux_builder():
    """Provide TmuxCommandBuilder for tests."""
    return TmuxCommandBuilder


@pytest.fixture
def mock_failed_subprocess_run(mocker):
    """Mock subprocess.run to simulate tmux command failures."""
    from subprocess import CompletedProcess

    def mock_run(cmd, **kwargs):
        if cmd[0] == "tmux":
            return CompletedProcess(cmd, 1, "", "no server running")
        return CompletedProcess(cmd, 0, "", "")

    return mocker.patch("subprocess.run", side_effect=mock_run)


@pytest.fixture
def claude_map_with_stale_entries(tmp_path):
    """Create a Claude map with some stale entries."""
    content = """main-session:%1:550e8400-e29b-41d4-a716-446655440000
old-session:%2:550e8400-e29b-41d4-a716-446655440001
main-session:%3:550e8400-e29b-41d4-a716-446655440002
deleted-session:%4:550e8400-e29b-41d4-a716-446655440003"""
    claude_map = tmp_path / ".tmux-claude-map"
    claude_map.write_text(content)
    return claude_map


@pytest.fixture
def incomplete_state_json():
    """State JSON with missing optional fields."""
    return {
        "created_at": "2025-08-24T12:00:00",
        "sessions": [
            {
                "name": "minimal",
                "windows": [
                    {"index": 1, "name": "work", "path": "/home/user", "ordinal": 0}
                ],
            }
        ],
        "current_session": None,
        "current_window_index": None,
        "claude": [],
    }


@pytest.fixture
def corrupted_state_json():
    """Corrupted JSON that should trigger error handling."""
    return '{"created_at": "2025-08-24T12:00:00", "sessions": [{'
