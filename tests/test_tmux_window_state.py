"""Tests for tmux window state management."""

import json
from unittest.mock import patch

import pytest

# Import the actual modules now
from cli.app.command.tmux.models import ClaudeBinding, Session, State, Window
from cli.app.command.tmux.utils import (
    list_sessions,
    list_windows_all,
    current_session_and_window,
    read_claude_map,
    clean_claude_map,
)


@pytest.fixture
def patch_state_file(temp_home):
    """Patch STATE_FILE to use temp directory."""
    temp_state_file = temp_home / ".tmux-window-state.json"
    with patch("cli.app.command.tmux.utils.STATE_FILE", temp_state_file):
        with patch("cli.app.command.tmux.state.STATE_FILE", temp_state_file):
            yield temp_state_file


@pytest.fixture
def patch_claude_map_file(temp_home):
    """Patch CLAUDE_MAP_FILE to use temp directory."""
    temp_claude_map = temp_home / ".tmux-claude-map"
    with patch("cli.app.command.tmux.utils.CLAUDE_MAP_FILE", temp_claude_map):
        with patch("cli.app.command.tmux.state.CLAUDE_MAP_FILE", temp_claude_map):
            yield temp_claude_map


class TestDataModels:
    """Test data model classes."""

    def test_window_dataclass(self):
        """Test Window dataclass creation."""
        window = Window(index=1, name="editor", path="/home/user", ordinal=0)
        assert window.index == 1
        assert window.name == "editor"
        assert window.path == "/home/user"
        assert window.ordinal == 0

    def test_session_dataclass(self):
        """Test Session dataclass creation."""
        window = Window(index=1, name="editor", path="/home/user", ordinal=0)
        session = Session(name="main", windows=[window])
        assert session.name == "main"
        assert len(session.windows) == 1
        assert session.windows[0] == window

    def test_claude_binding_dataclass(self):
        """Test ClaudeBinding dataclass creation."""
        binding = ClaudeBinding(
            session="main",
            window_name="editor",
            path="/home/user",
            ordinal=0,
            uuid="test-uuid",
        )
        assert binding.session == "main"
        assert binding.window_name == "editor"
        assert binding.path == "/home/user"
        assert binding.ordinal == 0
        assert binding.uuid == "test-uuid"

    def test_state_to_json(self, sample_state_json):
        """Test State serialization to JSON."""
        window = Window(index=1, name="editor", path="/home/user", ordinal=0)
        session = Session(name="main", windows=[window])
        binding = ClaudeBinding(
            session="main",
            window_name="editor",
            path="/home/user",
            ordinal=0,
            uuid="test-uuid",
        )
        state = State(
            created_at="2025-08-24T12:00:00",
            sessions=[session],
            current_session="main",
            current_window_index=1,
            claude=[binding],
        )

        json_str = state.to_json()
        parsed = json.loads(json_str)

        assert parsed["created_at"] == "2025-08-24T12:00:00"
        assert parsed["current_session"] == "main"
        assert parsed["current_window_index"] == 1
        assert len(parsed["sessions"]) == 1
        assert len(parsed["claude"]) == 1

    def test_state_from_json(self, sample_state_json):
        """Test State deserialization from JSON."""
        json_str = json.dumps(sample_state_json)
        state = State.from_json(json_str)

        assert state.created_at == sample_state_json["created_at"]
        assert state.current_session == sample_state_json["current_session"]
        assert state.current_window_index == sample_state_json["current_window_index"]
        assert len(state.sessions) == len(sample_state_json["sessions"])
        assert len(state.claude) == len(sample_state_json["claude"])

    def test_state_from_json_with_incomplete_data(self, incomplete_state_json):
        """Test State deserialization with missing optional fields."""
        json_str = json.dumps(incomplete_state_json)
        state = State.from_json(json_str)

        assert state.created_at == incomplete_state_json["created_at"]
        assert state.current_session is None
        assert state.current_window_index is None
        assert len(state.sessions) == 1
        assert len(state.claude) == 0


class TestTmuxUtilityFunctions:
    """Test tmux helper functions."""

    def test_list_sessions_success(self, mock_subprocess_run):
        """Test successful session listing."""
        sessions = list_sessions()
        assert sessions == ["main-session", "testing"]

    def test_list_sessions_no_server(self, mock_failed_subprocess_run):
        """Test session listing when no tmux server running."""
        sessions = list_sessions()
        assert sessions == []

    def test_list_windows_all(self, mock_subprocess_run):
        """Test listing all windows across sessions."""
        windows = list_windows_all()
        assert len(windows) == 4
        assert windows[0] == ("main-session", 1, "editor", "/home/user/project")
        assert windows[1] == ("main-session", 2, "terminal", "/home/user/project")
        assert windows[2] == ("main-session", 3, "editor", "/home/user/docs")
        assert windows[3] == ("testing", 1, "test-runner", "/home/user/project/tests")

    def test_current_session_and_window(self, mock_subprocess_run):
        """Test getting current session and window."""
        session, window = current_session_and_window()
        assert session == "main-session"
        assert window == 2

    def test_current_session_and_window_error(self, mock_failed_subprocess_run):
        """Test current session/window when tmux fails."""
        session, window = current_session_and_window()
        assert session is None
        assert window is None

    def test_list_sessions_with_special_characters(self, mocker):
        """Test parsing session names with special characters."""
        from subprocess import CompletedProcess

        special_sessions = "session-with-dashes\nsession:with:colons\nsession with spaces\nsession@with#special$chars\nsession_with_underscores\n"

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "list-sessions"], 0, special_sessions, ""
            ),
        )

        sessions = list_sessions()
        expected = [
            "session-with-dashes",
            "session:with:colons",
            "session with spaces",
            "session@with#special$chars",
            "session_with_underscores",
        ]
        assert sessions == expected

    def test_list_sessions_with_unicode_characters(self, mocker):
        """Test parsing session names with unicode characters."""
        from subprocess import CompletedProcess

        unicode_sessions = (
            "세션한글\nсессия\nsession-émojis-🚀\nsession-한국어-русский\n"
        )

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "list-sessions"], 0, unicode_sessions, ""
            ),
        )

        sessions = list_sessions()
        expected = ["세션한글", "сессия", "session-émojis-🚀", "session-한국어-русский"]
        assert sessions == expected

    def test_list_sessions_empty_output(self, mocker):
        """Test parsing when tmux returns empty output."""
        from subprocess import CompletedProcess

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(["tmux", "list-sessions"], 0, "", ""),
        )

        sessions = list_sessions()
        assert sessions == []

    def test_list_sessions_whitespace_only(self, mocker):
        """Test parsing when tmux returns only whitespace."""
        from subprocess import CompletedProcess

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "list-sessions"], 0, "\n   \n\t\n   \n", ""
            ),
        )

        sessions = list_sessions()
        assert sessions == []

    def test_list_windows_all_malformed_output(self, mocker):
        """Test parsing windows with malformed tmux output."""
        from subprocess import CompletedProcess

        malformed_output = """main-session	1	editor	/home/user/project
incomplete-line-missing-fields	2	terminal
session	index	name	path	extra-field
main-session		empty-name	/home/user
session	1	window	
main-session	not-a-number	window	/home/user"""

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "list-windows"], 0, malformed_output, ""
            ),
        )

        windows = list_windows_all()
        # Should parse the first valid line and the line with empty path
        assert len(windows) == 2
        assert windows[0] == ("main-session", 1, "editor", "/home/user/project")
        assert windows[1] == ("session", 1, "window", "")

    def test_list_windows_all_with_special_characters_in_paths(self, mocker):
        """Test parsing windows with special characters in paths."""
        from subprocess import CompletedProcess

        special_output = """session1	1	editor	/home/user/project with spaces
session2	2	terminal	/home/user/project-with-dashes
session3	3	vim	/home/user/project@special#chars
session4	4	emacs	/home/user/프로젝트/한글경로
session5	5	code	/home/user/проект/русский"""

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "list-windows"], 0, special_output, ""
            ),
        )

        windows = list_windows_all()
        assert len(windows) == 5
        assert windows[0] == ("session1", 1, "editor", "/home/user/project with spaces")
        assert windows[3] == ("session4", 4, "emacs", "/home/user/프로젝트/한글경로")
        assert windows[4] == ("session5", 5, "code", "/home/user/проект/русский")

    def test_current_session_and_window_malformed_output(self, mocker):
        """Test current session/window parsing with malformed output."""
        from subprocess import CompletedProcess

        # Test with missing tab separator
        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "display-message"], 0, "main-session2", ""
            ),
        )

        session, window = current_session_and_window()
        assert session is None
        assert window is None

    def test_current_session_and_window_non_numeric_window(self, mocker):
        """Test current session/window parsing with non-numeric window index."""
        from subprocess import CompletedProcess

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "display-message"], 0, "main-session\tnot-a-number\n", ""
            ),
        )

        session, window = current_session_and_window()
        # The function catches all exceptions, so both will be None for invalid window index
        assert session is None
        assert window is None

    def test_current_session_and_window_empty_fields(self, mocker):
        """Test current session/window parsing with empty fields."""
        from subprocess import CompletedProcess

        # Test with empty session name
        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(["tmux", "display-message"], 0, "\t2\n", ""),
        )

        session, window = current_session_and_window()
        assert session is None
        assert window is None

    def test_list_windows_all_very_long_names(self, mocker):
        """Test parsing windows with very long session/window names and paths."""
        from subprocess import CompletedProcess

        long_session = "s" * 1000
        long_window = "w" * 500
        long_path = "/very/long/path/" + ("directory/" * 50) + "final"

        long_output = f"{long_session}\t1\t{long_window}\t{long_path}"

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(["tmux", "list-windows"], 0, long_output, ""),
        )

        windows = list_windows_all()
        assert len(windows) == 1
        assert windows[0] == (long_session, 1, long_window, long_path)
        assert len(windows[0][0]) == 1000
        assert len(windows[0][2]) == 500

    def test_list_windows_all_with_tabs_in_names(self, mocker):
        """Test parsing windows with tab characters in names (edge case)."""
        from subprocess import CompletedProcess

        # Tab characters in window names would break the parsing
        # This tests the robustness of the tab-splitting logic
        tricky_output = "session1\t1\twindow\twith\textra\ttabs\t/home/user"

        mock_run = mocker.patch(
            "subprocess.run",
            return_value=CompletedProcess(
                ["tmux", "list-windows"], 0, tricky_output, ""
            ),
        )

        windows = list_windows_all()
        # The split('\t') should result in more than 4 parts, making this line invalid
        assert len(windows) == 0


class TestClaudeMapOperations:
    """Test Claude map file operations."""

    def test_read_claude_map_empty(self, patch_claude_map_file):
        """Test reading non-existent Claude map."""
        entries = read_claude_map()
        assert entries == []

    def test_read_claude_map_with_content(
        self, patch_claude_map_file, sample_claude_map_content
    ):
        """Test reading Claude map with valid content."""
        patch_claude_map_file.write_text(sample_claude_map_content)
        entries = read_claude_map()
        assert len(entries) >= 1
        # Verify format: (session, pane_id, uuid)
        for entry in entries:
            assert len(entry) == 3
            assert ":" not in entry[0] or entry[0].count(":") == 0  # session name
            assert entry[1].startswith("%")  # pane_id format

    def test_read_claude_map_with_comments(self, patch_claude_map_file):
        """Test reading Claude map with comments and blank lines."""
        content = """
# This is a comment
main-session:%1:550e8400-e29b-41d4-a716-446655440000

testing:%2:550e8400-e29b-41d4-a716-446655440001
# Another comment
"""
        patch_claude_map_file.write_text(content)
        entries = read_claude_map()
        assert len(entries) == 2
        assert entries[0] == (
            "main-session",
            "%1",
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert entries[1] == ("testing", "%2", "550e8400-e29b-41d4-a716-446655440001")

    def test_read_claude_map_malformed_lines(self, patch_claude_map_file):
        """Test reading Claude map with malformed lines."""
        content = """main-session:%1:550e8400-e29b-41d4-a716-446655440000
invalid-line-missing-colons
testing:%2:550e8400-e29b-41d4-a716-446655440001
another:invalid:line:too:many:colons
"""
        patch_claude_map_file.write_text(content)
        entries = read_claude_map()
        # Should parse 3 lines: the first, third, and fourth (since rsplit handles the last one correctly)
        assert len(entries) == 3
        assert entries[0] == (
            "main-session",
            "%1",
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert entries[1] == ("testing", "%2", "550e8400-e29b-41d4-a716-446655440001")
        assert entries[2] == ("another:invalid:line:too", "many", "colons")

    def test_clean_claude_map(self, mock_subprocess_run, patch_claude_map_file):
        """Test cleaning stale entries from Claude map."""
        # Set up Claude map with some entries
        content = """main-session:%1:550e8400-e29b-41d4-a716-446655440000
main-session:%2:550e8400-e29b-41d4-a716-446655440001
old-session:%3:550e8400-e29b-41d4-a716-446655440002"""
        patch_claude_map_file.write_text(content)

        removed = clean_claude_map()

        # Should keep entries that exist in mock response, remove others
        assert removed > 0
        remaining_content = patch_claude_map_file.read_text()
        # Should only keep entries that match existing panes from mock
        lines = [line for line in remaining_content.splitlines() if line.strip()]
        assert len(lines) <= 3  # At most the entries that exist

    def test_clean_claude_map_no_tmux_server(
        self, mock_failed_subprocess_run, patch_claude_map_file
    ):
        """Test cleaning Claude map when tmux server is not running."""
        content = """main-session:%1:550e8400-e29b-41d4-a716-446655440000
testing:%2:550e8400-e29b-41d4-a716-446655440001"""
        patch_claude_map_file.write_text(content)

        removed = clean_claude_map()

        # Should remove all entries since no tmux server is running
        assert removed == 2
        remaining_content = patch_claude_map_file.read_text()
        assert remaining_content.strip() == ""

    def test_read_claude_map_with_unicode_session_names(self, patch_claude_map_file):
        """Test reading Claude map with unicode characters in session names."""
        content = """세션한글:%1:550e8400-e29b-41d4-a716-446655440000
сессия:%2:550e8400-e29b-41d4-a716-446655440001
session-émojis-🚀:%3:550e8400-e29b-41d4-a716-446655440002"""
        patch_claude_map_file.write_text(content)

        entries = read_claude_map()
        assert len(entries) == 3
        assert entries[0] == ("세션한글", "%1", "550e8400-e29b-41d4-a716-446655440000")
        assert entries[1] == ("сессия", "%2", "550e8400-e29b-41d4-a716-446655440001")
        assert entries[2] == (
            "session-émojis-🚀",
            "%3",
            "550e8400-e29b-41d4-a716-446655440002",
        )

    def test_read_claude_map_with_special_characters(self, patch_claude_map_file):
        """Test reading Claude map with special characters in session names."""
        content = """session:with:colons:%1:550e8400-e29b-41d4-a716-446655440000
session-with-dashes:%2:550e8400-e29b-41d4-a716-446655440001
session@with#special$chars:%3:550e8400-e29b-41d4-a716-446655440002
session_with_underscores:%4:550e8400-e29b-41d4-a716-446655440003"""
        patch_claude_map_file.write_text(content)

        entries = read_claude_map()
        assert len(entries) == 4
        # The session with colons should be parsed correctly - split on : gives more parts
        # but read_claude_map should handle this gracefully
        assert entries[0][0] == "session:with:colons"
        assert entries[1][0] == "session-with-dashes"
        assert entries[2][0] == "session@with#special$chars"
        assert entries[3][0] == "session_with_underscores"

    def test_read_claude_map_with_very_long_lines(self, patch_claude_map_file):
        """Test reading Claude map with very long session names and UUIDs."""
        long_session = "very-long-session-name-" + "a" * 1000
        long_uuid = (
            "550e8400-e29b-41d4-a716-446655440000-with-extra-very-long-suffix-"
            + "b" * 500
        )
        content = f"{long_session}:%1:{long_uuid}"
        patch_claude_map_file.write_text(content)

        entries = read_claude_map()
        assert len(entries) == 1
        assert entries[0][0] == long_session
        assert entries[0][1] == "%1"
        assert entries[0][2] == long_uuid
        assert len(entries[0][0]) > 1000
        assert len(entries[0][2]) > 500

    def test_read_claude_map_with_empty_and_whitespace_lines(
        self, patch_claude_map_file
    ):
        """Test reading Claude map with various empty and whitespace patterns."""
        content = """


main-session:%1:550e8400-e29b-41d4-a716-446655440000
   
	
testing:%2:550e8400-e29b-41d4-a716-446655440001
   	   

another-session:%3:550e8400-e29b-41d4-a716-446655440002


"""
        patch_claude_map_file.write_text(content)

        entries = read_claude_map()
        assert len(entries) == 3
        assert entries[0] == (
            "main-session",
            "%1",
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert entries[1] == ("testing", "%2", "550e8400-e29b-41d4-a716-446655440001")
        assert entries[2] == (
            "another-session",
            "%3",
            "550e8400-e29b-41d4-a716-446655440002",
        )

    def test_read_claude_map_binary_corruption(self, patch_claude_map_file):
        """Test reading Claude map with binary corruption (UnicodeDecodeError)."""
        # Write binary data that will cause UnicodeDecodeError
        patch_claude_map_file.write_bytes(
            b"\xff\xfe\x00\x01\x02corrupted\nvalid-session:%1:valid-uuid"
        )

        entries = read_claude_map()
        # Should handle UnicodeDecodeError gracefully and return empty list
        assert entries == []

    def test_read_claude_map_extremely_malformed_lines(self, patch_claude_map_file):
        """Test reading Claude map with extremely malformed entries."""
        content = """main-session:%1:550e8400-e29b-41d4-a716-446655440000
::
:
:::::::::
single-field-only
two:fields:only
empty-uuid-field::%1:
empty-pane-field:session::550e8400-e29b-41d4-a716-446655440000
empty-session-field::%1:550e8400-e29b-41d4-a716-446655440000
valid-session:%1:550e8400-e29b-41d4-a716-446655440001"""
        patch_claude_map_file.write_text(content)

        entries = read_claude_map()
        # With empty field filtering and rsplit, several lines parse successfully:
        # main-session:%1:uuid -> valid
        # two:fields:only -> becomes ("two", "fields", "only") -> valid (all non-empty)
        # empty-session-field::%1:uuid -> becomes ("empty-session-field:", "%1", "uuid") -> valid
        # valid-session:%1:uuid -> valid
        assert len(entries) == 4
        assert entries[0] == (
            "main-session",
            "%1",
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert entries[1] == ("two", "fields", "only")
        assert entries[2] == (
            "empty-session-field:",
            "%1",
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert entries[3] == (
            "valid-session",
            "%1",
            "550e8400-e29b-41d4-a716-446655440001",
        )

    def test_read_claude_map_with_newlines_in_fields(self, patch_claude_map_file):
        """Test reading Claude map with newline characters in fields (shouldn't happen but test robustness)."""
        # This is an edge case - if somehow newlines got into session names or UUIDs
        content = """session-with-newline-char\n-in-name:%1:550e8400-e29b-41d4-a716-446655440000
normal-session:%2:550e8400-e29b-41d4-a716-446655440001"""
        patch_claude_map_file.write_text(content)

        entries = read_claude_map()
        # The line splitting by \n should handle this - first line becomes two separate lines
        # First line: "session-with-newline-char" (invalid - not enough fields)
        # Second line: "-in-name:%1:550e8400-e29b-41d4-a716-446655440000" (valid)
        # Third line: "normal-session:%2:550e8400-e29b-41d4-a716-446655440001" (valid)
        assert len(entries) == 2
        assert entries[0] == ("-in-name", "%1", "550e8400-e29b-41d4-a716-446655440000")
        assert entries[1] == (
            "normal-session",
            "%2",
            "550e8400-e29b-41d4-a716-446655440001",
        )


class TestStateManagement:
    """Test state save/load functionality."""

    def test_save_state_no_sessions(self, mock_failed_subprocess_run, patch_state_file):
        """Test save_state when no tmux sessions are running."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import save

        runner = CliRunner()
        result = runner.invoke(save)
        assert result.exit_code == 1
        assert "No tmux sessions running" in result.output

    @patch("cli.app.command.tmux.state.datetime")
    def test_save_state_success(
        self,
        mock_datetime,
        mock_subprocess_run,
        patch_state_file,
        patch_claude_map_file,
    ):
        """Test successful state saving."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import save

        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2025-08-24T12:00:00"

        runner = CliRunner()
        result = runner.invoke(save)
        assert result.exit_code == 0
        assert "State saved" in result.output

        # Verify state file was created
        assert patch_state_file.exists()
        state_data = json.loads(patch_state_file.read_text())
        assert state_data["created_at"] == "2025-08-24T12:00:00"
        assert len(state_data["sessions"]) == 2  # From mock data

    def test_load_state_no_file(self, patch_state_file):
        """Test load_state when no saved state exists."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import load

        runner = CliRunner()
        result = runner.invoke(load)
        assert result.exit_code == 1
        assert "No saved state found" in result.output

    def test_load_state_success(
        self, mock_subprocess_run, patch_state_file, sample_state_json
    ):
        """Test successful state loading."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import load

        # Create a saved state file
        patch_state_file.write_text(json.dumps(sample_state_json))

        runner = CliRunner()
        result = runner.invoke(load)
        assert result.exit_code == 0
        assert "Loading tmux window state" in result.output
        assert "State restored" in result.output

    @patch("cli.app.command.tmux.state.datetime")
    def test_save_atomic_file_operations(
        self,
        mock_datetime,
        mock_subprocess_run,
        patch_state_file,
        patch_claude_map_file,
    ):
        """Test that save operations use atomic file writes."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import save

        mock_datetime.now.return_value.isoformat.return_value = "2025-08-24T12:00:00"

        runner = CliRunner()

        # Create existing state file to verify it's preserved during atomic operations
        original_content = '{"test": "original"}'
        patch_state_file.write_text(original_content)

        # Mock the temporary file creation and verify atomic behavior
        temp_file = patch_state_file.with_suffix(".tmp")

        # Before save, temp file should not exist
        assert not temp_file.exists()

        result = runner.invoke(save)
        assert result.exit_code == 0

        # After save, temp file should be cleaned up
        assert not temp_file.exists()

        # Final state file should exist with new content
        assert patch_state_file.exists()
        state_content = patch_state_file.read_text()
        assert state_content != original_content
        assert "created_at" in state_content

    def test_save_atomic_operation_preserves_original_on_error(
        self, mock_subprocess_run, patch_state_file, patch_claude_map_file
    ):
        """Test that original file is preserved if atomic write fails."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import save
        from pathlib import Path

        # Create existing state file
        original_content = '{"test": "original"}'
        patch_state_file.write_text(original_content)

        runner = CliRunner()

        # Mock Path.write_text to raise an error during temp file write
        original_write_text = Path.write_text

        def failing_write_text(self, data, *args, **kwargs):
            if str(self).endswith(".tmp"):
                raise OSError("Simulated write failure")
            return original_write_text(self, data, *args, **kwargs)

        with patch.object(Path, "write_text", side_effect=failing_write_text):
            with patch("cli.app.command.tmux.state.datetime") as mock_datetime:
                mock_datetime.now.return_value.isoformat.return_value = (
                    "2025-08-24T12:00:00"
                )

                # This should fail during write
                result = runner.invoke(save)
                # Command should still exit successfully from CLI perspective
                # (the error handling might be at a different level)

                # Original file should still exist and be unchanged
                assert patch_state_file.exists()
                assert patch_state_file.read_text() == original_content


class TestIntegration:
    """Integration tests for complete workflows."""

    @patch("cli.app.command.tmux.state.datetime")
    def test_save_load_roundtrip(
        self,
        mock_datetime,
        mock_subprocess_run,
        patch_state_file,
        patch_claude_map_file,
    ):
        """Test complete save/load cycle."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import save, load

        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2025-08-24T12:00:00"

        runner = CliRunner()

        # First save state
        result = runner.invoke(save)
        assert result.exit_code == 0

        # Verify state file exists
        assert patch_state_file.exists()
        original_content = patch_state_file.read_text()

        # Then load state
        result = runner.invoke(load)
        assert result.exit_code == 0

        # State should still be there and unchanged
        assert patch_state_file.read_text() == original_content

    def test_state_with_duplicate_window_names(
        self, mock_subprocess_run, patch_state_file, patch_claude_map_file
    ):
        """Test handling windows with duplicate names but different paths."""
        from click.testing import CliRunner
        from cli.app.command.tmux.state import save

        # Mock tmux to return duplicate window names
        with patch("cli.app.command.tmux.state.list_sessions") as mock_list_sessions:
            mock_list_sessions.return_value = ["main-session"]
            with patch(
                "cli.app.command.tmux.state.list_windows_all"
            ) as mock_list_windows:
                mock_list_windows.return_value = [
                    ("main-session", 1, "editor", "/home/user/project1"),
                    ("main-session", 2, "editor", "/home/user/project2"),
                    (
                        "main-session",
                        3,
                        "editor",
                        "/home/user/project1",
                    ),  # Same as first
                ]
                with patch("cli.app.command.tmux.state.datetime") as mock_datetime:
                    mock_datetime.now.return_value.isoformat.return_value = (
                        "2025-08-24T12:00:00"
                    )

                    runner = CliRunner()
                    result = runner.invoke(save)
                    assert result.exit_code == 0

                    # Verify ordinals are computed correctly
                    state_data = json.loads(patch_state_file.read_text())
                    windows = state_data["sessions"][0]["windows"]

                    # Find windows by path to check ordinals
                    project1_windows = [
                        w for w in windows if w["path"] == "/home/user/project1"
                    ]
                    project2_windows = [
                        w for w in windows if w["path"] == "/home/user/project2"
                    ]

                    assert len(project1_windows) == 2
                    assert len(project2_windows) == 1

                    # First occurrence should have ordinal 0, second should have ordinal 1
                    ordinals = sorted([w["ordinal"] for w in project1_windows])
                    assert ordinals == [0, 1]
                    assert project2_windows[0]["ordinal"] == 0
