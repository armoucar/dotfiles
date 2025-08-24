"""Tests for tmux-window-state script."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the script by executing it
script_path = Path(__file__).parent.parent / "bin" / "tmux-window-state"
script_globals = {}
with open(script_path) as f:
    exec(f.read(), script_globals)


# Create a mock module object
class MockModule:
    pass


tws = MockModule()
for name, value in script_globals.items():
    if not name.startswith(
        "__"
    ):  # Include single underscore functions, exclude dunder methods
        setattr(tws, name, value)


@pytest.fixture
def patch_claude_map_file():
    """Context manager to properly patch CLAUDE_MAP_FILE global variable."""

    def _patch(claude_map_path):
        original = script_globals["CLAUDE_MAP_FILE"]
        script_globals["CLAUDE_MAP_FILE"] = claude_map_path
        try:
            yield claude_map_path
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original

    return _patch


class TestDataModels:
    """Test the data classes and their serialization."""

    def test_window_creation(self):
        """Test Window dataclass creation."""
        window = tws.Window(index=1, name="editor", path="/home/user", ordinal=0)
        assert window.index == 1
        assert window.name == "editor"
        assert window.path == "/home/user"
        assert window.ordinal == 0

    def test_session_creation(self):
        """Test Session dataclass creation."""
        windows = [tws.Window(1, "editor", "/home/user", 0)]
        session = tws.Session(name="main", windows=windows)
        assert session.name == "main"
        assert len(session.windows) == 1
        assert session.windows[0].name == "editor"

    def test_claude_binding_creation(self):
        """Test ClaudeBinding dataclass creation."""
        binding = tws.ClaudeBinding(
            session="main",
            window_name="editor",
            path="/home/user",
            ordinal=0,
            uuid="test-uuid",
        )
        assert binding.session == "main"
        assert binding.window_name == "editor"
        assert binding.uuid == "test-uuid"


class TestStateClass:
    """Test the State class serialization and deserialization."""

    def test_state_to_json(self, sample_state_json):
        """Test State serialization to JSON."""
        # Create State object from sample data
        sessions = []
        for s_data in sample_state_json["sessions"]:
            windows = [tws.Window(**w) for w in s_data["windows"]]
            sessions.append(tws.Session(name=s_data["name"], windows=windows))

        claude = [tws.ClaudeBinding(**c) for c in sample_state_json["claude"]]

        state = tws.State(
            created_at=sample_state_json["created_at"],
            sessions=sessions,
            current_session=sample_state_json["current_session"],
            current_window_index=sample_state_json["current_window_index"],
            claude=claude,
        )

        # Test serialization
        json_output = state.to_json()
        parsed = json.loads(json_output)

        assert parsed["created_at"] == "2025-08-24T12:00:00"
        assert len(parsed["sessions"]) == 2
        assert parsed["current_session"] == "main-session"
        assert len(parsed["claude"]) == 2

    def test_state_from_json(self, sample_state_json):
        """Test State deserialization from JSON."""
        json_str = json.dumps(sample_state_json)
        state = tws.State.from_json(json_str)

        assert state.created_at == "2025-08-24T12:00:00"
        assert len(state.sessions) == 2
        assert state.sessions[0].name == "main-session"
        assert len(state.sessions[0].windows) == 3
        assert state.current_session == "main-session"
        assert state.current_window_index == 2
        assert len(state.claude) == 2
        assert state.claude[0].uuid == "550e8400-e29b-41d4-a716-446655440000"

    def test_state_from_json_with_missing_fields(self, incomplete_state_json):
        """Test State deserialization with missing optional fields."""
        json_str = json.dumps(incomplete_state_json)
        state = tws.State.from_json(json_str)

        assert state.current_session is None
        assert state.current_window_index is None
        assert len(state.claude) == 0

    def test_state_from_json_invalid(self, corrupted_state_json):
        """Test State deserialization with invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            tws.State.from_json(corrupted_state_json)


class TestTmuxHelpers:
    """Test helper functions that interact with tmux."""

    def test_list_sessions_success(self, mock_subprocess_run):
        """Test successful session listing."""
        sessions = tws._list_sessions()
        assert sessions == ["main-session", "testing"]

    def test_list_sessions_no_server(self, mock_failed_subprocess_run):
        """Test session listing when no tmux server is running."""
        sessions = tws._list_sessions()
        assert sessions == []

    def test_list_windows_all(self, mock_subprocess_run):
        """Test listing all windows across sessions."""
        windows = tws._list_windows_all()

        expected = [
            ("main-session", 1, "editor", "/home/user/project"),
            ("main-session", 2, "terminal", "/home/user/project"),
            ("main-session", 3, "editor", "/home/user/docs"),
            ("testing", 1, "test-runner", "/home/user/project/tests"),
        ]
        assert windows == expected

    def test_current_session_and_window(self, mock_subprocess_run):
        """Test getting current session and window."""
        session, window = tws._current_session_and_window()
        assert session == "main-session"
        assert window == 2

    def test_current_session_and_window_error(self, mock_failed_subprocess_run):
        """Test getting current session when tmux command fails."""
        session, window = tws._current_session_and_window()
        assert session is None
        assert window is None


class TestClaudeMapFunctions:
    """Test Claude mapping file operations."""

    def test_read_claude_map_empty(self, temp_home):
        """Test reading Claude map when file doesn't exist."""
        claude_map = temp_home / ".tmux-claude-map"
        original = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            entries = tws._read_claude_map()
            assert entries == []
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original

    def test_read_claude_map_with_data(self, temp_home, sample_claude_map_content):
        """Test reading Claude map with valid data."""
        claude_map = temp_home / ".tmux-claude-map"
        claude_map.write_text(sample_claude_map_content)

        original = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            entries = tws._read_claude_map()
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original

        expected = [
            ("main-session", "%1", "550e8400-e29b-41d4-a716-446655440000"),
            ("testing", "%2", "550e8400-e29b-41d4-a716-446655440001"),
            ("main-session", "%3", "550e8400-e29b-41d4-a716-446655440002"),
        ]
        assert entries == expected

    def test_read_claude_map_with_comments_and_empty_lines(self, temp_home):
        """Test reading Claude map with comments and empty lines."""
        content = """# This is a comment
main-session:%1:uuid1

testing:%2:uuid2
# Another comment
"""
        claude_map = temp_home / ".tmux-claude-map"
        claude_map.write_text(content)

        original = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            entries = tws._read_claude_map()
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original

        assert len(entries) == 2
        assert entries[0] == ("main-session", "%1", "uuid1")
        assert entries[1] == ("testing", "%2", "uuid2")

    def test_read_claude_map_malformed_entries(self, temp_home):
        """Test reading Claude map with malformed entries."""
        content = """valid-session:%1:uuid1
invalid-entry-missing-parts
another:valid:%2:uuid2:extra
"""
        claude_map = temp_home / ".tmux-claude-map"
        claude_map.write_text(content)

        original = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            entries = tws._read_claude_map()
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original

        # Should include entries with exactly 3 parts (after split(":", 2))
        assert len(entries) == 2
        assert entries[0] == ("valid-session", "%1", "uuid1")
        assert entries[1] == (
            "another",
            "valid",
            "%2:uuid2:extra",
        )  # This is valid with split(":", 2)

    def test_clean_claude_map(self, temp_home, mock_subprocess_run):
        """Test cleaning stale entries from Claude map."""
        # Create Claude map with some stale entries
        content = """main-session:%1:uuid1
stale-session:%2:uuid2
main-session:%3:uuid3"""
        claude_map = temp_home / ".tmux-claude-map"
        claude_map.write_text(content)

        # Mock list-panes to show only some panes exist
        original = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            with patch.object(tws, "tmux") as mock_tmux:
                mock_tmux.return_value = "main-session:%1\nmain-session:%3\n"
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    removed = tws._clean_claude_map()
                finally:
                    script_globals["tmux"] = original_tmux
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original

        assert removed == 1  # One stale entry removed

        # Check file contents
        remaining_content = claude_map.read_text().strip()
        lines = remaining_content.split("\n")
        assert len(lines) == 2
        assert "main-session:%1:uuid1" in lines
        assert "main-session:%3:uuid3" in lines


class TestSaveState:
    """Test the save_state functionality."""

    def test_save_state_no_sessions(self, mock_failed_subprocess_run, temp_home):
        """Test save_state when no tmux sessions are running."""
        with patch.object(tws, "STATE_FILE", temp_home / "state.json"):
            with pytest.raises(SystemExit) as exc_info:
                tws.save_state()
            assert exc_info.value.code == 1

    def test_save_state_success(
        self, mock_subprocess_run, mock_datetime_now, temp_home
    ):
        """Test successful state saving."""
        state_file = temp_home / "state.json"
        claude_map = temp_home / ".tmux-claude-map"

        # Create some Claude map entries
        claude_map.write_text("main-session:%1:test-uuid-1\n")

        original_state = script_globals["STATE_FILE"]
        original_claude_map = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            # Mock the pane info query to return valid data
            with patch.object(tws, "tmux") as mock_tmux:

                def mock_tmux_side_effect(*args):
                    if args[0] == "list-sessions":
                        return "main-session\ntesting\n"
                    elif args[0] == "list-windows":
                        return "main-session\t1\teditor\t/home/user/project\nmain-session\t2\tterminal\t/home/user/project\ntesting\t1\ttest-runner\t/home/user/project/tests\n"
                    elif args[0] == "display-message" and args[1] == "-p":
                        if args[2] == "#{session_name}\\t#{window_index}":
                            return "main-session\t1\n"
                        elif args[3] == "%1":
                            return "main-session\teditor\t/home/user/project\t1\n"
                    elif args[0] == "list-panes":
                        return "main-session:%1\n"
                    return ""

                mock_tmux.side_effect = mock_tmux_side_effect
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    tws.save_state()
                finally:
                    script_globals["tmux"] = original_tmux
        finally:
            script_globals["STATE_FILE"] = original_state
            script_globals["CLAUDE_MAP_FILE"] = original_claude_map

        # Verify state file was created
        assert state_file.exists()

        # Verify state contents
        state_data = json.loads(state_file.read_text())
        assert state_data["created_at"] == "2025-08-24T12:00:00"
        assert len(state_data["sessions"]) >= 1

    def test_save_state_with_incomplete_pane_info(self, mock_subprocess_run, temp_home):
        """Test save_state handles panes with incomplete information."""
        state_file = temp_home / "state.json"
        claude_map = temp_home / ".tmux-claude-map"

        # Create Claude map with pane that has incomplete info
        claude_map.write_text("session:%1:uuid1\n")

        original_state = script_globals["STATE_FILE"]
        original_claude_map = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            script_globals["CLAUDE_MAP_FILE"] = claude_map

            with patch.object(tws, "tmux") as mock_tmux:

                def mock_side_effect(*args):
                    if "display-message" in args and "%1" in args:
                        # Return incomplete pane info (empty fields)
                        return "\t\t\t\n"
                    elif args[0] == "list-sessions":
                        return "session\n"
                    elif args[0] == "list-windows":
                        return "session\t1\twindow\t/path\n"
                    elif "#{session_name}\\t#{window_index}" in str(args):
                        return "session\t1\n"
                    elif args[0] == "list-panes":
                        return "session:%1\n"
                    return ""

                mock_tmux.side_effect = mock_side_effect
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    tws.save_state()
                finally:
                    script_globals["tmux"] = original_tmux
        finally:
            script_globals["STATE_FILE"] = original_state
            script_globals["CLAUDE_MAP_FILE"] = original_claude_map

        # Should complete without error, skipping the invalid pane
        assert state_file.exists()


class TestLoadState:
    """Test the load_state functionality."""

    def test_load_state_no_file(self, temp_home):
        """Test load_state when no state file exists."""
        original = script_globals["STATE_FILE"]
        try:
            script_globals["STATE_FILE"] = temp_home / "nonexistent.json"
            with pytest.raises(SystemExit) as exc_info:
                tws.load_state()
            assert exc_info.value.code == 1
        finally:
            script_globals["STATE_FILE"] = original

    def test_load_state_success(
        self, mock_subprocess_run, temp_home, sample_state_json
    ):
        """Test successful state loading."""
        state_file = temp_home / "state.json"
        state_file.write_text(json.dumps(sample_state_json))

        original = script_globals["STATE_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            with patch.object(tws, "tmux") as mock_tmux:
                # Mock tmux commands for loading
                def mock_side_effect(*args):
                    if args[0] == "has-session":
                        return ""  # Session exists
                    elif (
                        args[0] == "list-windows"
                        and len(args) > 3
                        and "#{window_index}" in str(args)
                        and "#{window_id}" in str(args)
                    ):
                        # This is the _window_id_for call
                        return "1\t@1\n2\t@2\n3\t@3\n"
                    elif args[0] == "list-windows" and "#{window_index}" in str(args):
                        return "1\n2\n3\n"
                    return ""

                mock_tmux.side_effect = mock_side_effect
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    tws.load_state()
                finally:
                    script_globals["tmux"] = original_tmux

                # Should complete without errors
                # Verify tmux commands were called appropriately
                mock_tmux.assert_called()
        finally:
            script_globals["STATE_FILE"] = original

    def test_load_state_with_claude_sessions(
        self, mock_subprocess_run, temp_home, sample_state_json
    ):
        """Test load_state resuming Claude sessions."""
        state_file = temp_home / "state.json"
        state_file.write_text(json.dumps(sample_state_json))

        original = script_globals["STATE_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            with patch.object(tws, "tmux") as mock_tmux:
                # Track Claude resume commands
                claude_resume_calls = []

                def mock_side_effect(*args):
                    if args[0] == "send-keys" and "claude --resume" in str(args):
                        claude_resume_calls.append(args)
                    elif args[0] == "has-session":
                        return ""
                    elif (
                        args[0] == "list-windows"
                        and len(args) > 3
                        and "#{window_index}" in str(args)
                        and "#{window_id}" in str(args)
                    ):
                        # This is the _window_id_for call
                        return "1\t@1\n2\t@2\n3\t@3\n"
                    elif args[0] == "list-windows" and "#{window_index}" in str(args):
                        return "1\n2\n3\n"
                    return ""

                mock_tmux.side_effect = mock_side_effect
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    tws.load_state()
                finally:
                    script_globals["tmux"] = original_tmux

                # Should have attempted to resume Claude sessions
                assert len(claude_resume_calls) >= 1
        finally:
            script_globals["STATE_FILE"] = original

        # Verify Claude resume command format
        claude_call = next(
            call for call in claude_resume_calls if "claude --resume" in str(call)
        )
        assert "550e8400-e29b-41d4-a716-446655440000" in str(
            claude_call
        ) or "550e8400-e29b-41d4-a716-446655440001" in str(claude_call)


class TestHelperFunctions:
    """Test utility functions."""

    def test_window_id_for(self, mock_subprocess_run):
        """Test _window_id_for function."""
        with patch.object(tws, "tmux") as mock_tmux:
            mock_tmux.return_value = "1\t@1\n2\t@2\n3\t@3\n"
            # Also patch the function in script_globals
            original_tmux = script_globals["tmux"]
            script_globals["tmux"] = mock_tmux
            try:
                window_id = tws._window_id_for("main-session", 2)
                assert window_id == "@2"
            finally:
                script_globals["tmux"] = original_tmux

    def test_window_id_for_not_found(self, mock_subprocess_run):
        """Test _window_id_for when window index doesn't exist."""
        with patch.object(tws, "tmux") as mock_tmux:
            mock_tmux.return_value = "1\t@1\n3\t@3\n"
            window_id = tws._window_id_for("main-session", 2)
            assert window_id is None

    def test_new_window_get_id(self, mock_subprocess_run):
        """Test _new_window_get_id function."""
        with patch.object(tws, "tmux") as mock_tmux:
            mock_tmux.return_value = "@4\n"
            # Also patch the function in script_globals
            original_tmux = script_globals["tmux"]
            script_globals["tmux"] = mock_tmux
            try:
                window_id = tws._new_window_get_id(
                    "main-session", "new-window", "/path"
                )
                assert window_id == "@4"
            finally:
                script_globals["tmux"] = original_tmux


class TestMainFunction:
    """Test the main function and argument parsing."""

    def test_main_save_command(self, mock_subprocess_run, mock_datetime_now, temp_home):
        """Test main function with save command."""
        state_file = temp_home / "state.json"
        claude_map = temp_home / ".tmux-claude-map"
        claude_map.write_text("")  # Empty Claude map

        original_state = script_globals["STATE_FILE"]
        original_claude_map = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            result = tws.main(["save"])
            assert result == 0
            assert state_file.exists()
        finally:
            script_globals["STATE_FILE"] = original_state
            script_globals["CLAUDE_MAP_FILE"] = original_claude_map

    def test_main_show_command_no_file(self, temp_home, capsys):
        """Test main function with show command when no state file exists."""
        original = script_globals["STATE_FILE"]
        try:
            script_globals["STATE_FILE"] = temp_home / "nonexistent.json"
            result = tws.main(["show"])
            assert result == 0

            captured = capsys.readouterr()
            assert "No saved state" in captured.out
        finally:
            script_globals["STATE_FILE"] = original

    def test_main_show_command_with_file(self, temp_home, sample_state_json, capsys):
        """Test main function with show command when state file exists."""
        state_file = temp_home / "state.json"
        state_file.write_text(json.dumps(sample_state_json, indent=2))

        original = script_globals["STATE_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            result = tws.main(["show"])
            assert result == 0

            captured = capsys.readouterr()
            assert "main-session" in captured.out
            assert "editor" in captured.out
        finally:
            script_globals["STATE_FILE"] = original

    def test_main_cleanup_command(self, mock_subprocess_run, temp_home, capsys):
        """Test main function with cleanup command."""
        claude_map = temp_home / ".tmux-claude-map"
        claude_map.write_text("session:%1:uuid1\nstale:%2:uuid2\n")

        original_claude_map = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            with patch.object(tws, "tmux") as mock_tmux:
                mock_tmux.return_value = "session:%1\n"  # Only first pane exists
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    result = tws.main(["cleanup"])
                    assert result == 0
                finally:
                    script_globals["tmux"] = original_tmux

                captured = capsys.readouterr()
                assert "Removed 1 stale mapping(s)" in captured.out
        finally:
            script_globals["CLAUDE_MAP_FILE"] = original_claude_map


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration-style tests that test complete workflows."""

    def test_save_and_load_roundtrip(
        self, mock_subprocess_run, mock_datetime_now, temp_home
    ):
        """Test complete save -> load workflow."""
        state_file = temp_home / "state.json"
        claude_map = temp_home / ".tmux-claude-map"

        # Setup initial state
        claude_map.write_text("main:%1:uuid1\n")

        original_state = script_globals["STATE_FILE"]
        original_claude_map = script_globals["CLAUDE_MAP_FILE"]
        try:
            script_globals["STATE_FILE"] = state_file
            script_globals["CLAUDE_MAP_FILE"] = claude_map
            with patch.object(tws, "tmux") as mock_tmux:
                # Setup mock for save
                def save_mock_side_effect(*args):
                    if args[0] == "list-sessions":
                        return "main\n"
                    elif args[0] == "list-windows":
                        return "main\t1\twork\t/home/user\n"
                    elif (
                        args[0] == "display-message"
                        and "#{session_name}\\t#{window_index}" in str(args)
                    ):
                        return "main\t1\n"
                    elif args[0] == "display-message" and "%1" in args:
                        return "main\twork\t/home/user\t1\n"
                    elif args[0] == "list-panes":
                        return "main:%1\n"
                    return ""

                mock_tmux.side_effect = save_mock_side_effect
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux
                try:
                    # Save state
                    result = tws.main(["save"])
                    assert result == 0
                    assert state_file.exists()

                    # Reset mock for load
                    mock_tmux.reset_mock()

                    def load_mock_side_effect(*args):
                        if args[0] == "has-session":
                            return ""
                        elif (
                            args[0] == "list-windows"
                            and len(args) > 3
                            and "#{window_index}" in str(args)
                            and "#{window_id}" in str(args)
                        ):
                            # This is the _window_id_for call
                            return "1\t@1\n"
                        elif args[0] == "list-windows" and "#{window_index}" in str(
                            args
                        ):
                            return "1\n"
                        return ""

                    mock_tmux.side_effect = load_mock_side_effect

                    # Load state
                    result = tws.main(["load"])
                    assert result == 0
                finally:
                    script_globals["tmux"] = original_tmux
        finally:
            script_globals["STATE_FILE"] = original_state
            script_globals["CLAUDE_MAP_FILE"] = original_claude_map

        # Both operations should succeed
        assert state_file.exists()

        # Verify state content
        state_data = json.loads(state_file.read_text())
        assert len(state_data["sessions"]) >= 1
        assert len(state_data["claude"]) >= 1
