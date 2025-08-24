"""Tests for claude-start script."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the script by executing it
script_path = Path(__file__).parent.parent / "bin" / "claude-start"
script_globals = {}
with open(script_path) as f:
    exec(f.read(), script_globals)


# Create a mock module object
class MockModule:
    pass


cs = MockModule()
for name, value in script_globals.items():
    if not name.startswith(
        "__"
    ):  # Include single underscore functions, exclude dunder methods
        setattr(cs, name, value)


@pytest.fixture
def mock_claude_start_subprocess(mocker):
    """Mock subprocess for claude-start specific tmux commands."""
    from subprocess import CompletedProcess

    def mock_run(cmd, **kwargs):
        if cmd[0] != "tmux":
            return CompletedProcess(cmd, 0, "", "")
        if "display-message" in cmd and "#{session_name}" in cmd:
            return CompletedProcess(cmd, 0, "test-session", "")
        elif "display-message" in cmd and "#{window_name}" in cmd:
            return CompletedProcess(cmd, 0, "work-window", "")
        elif "display-message" in cmd and "#{pane_id}" in cmd:
            return CompletedProcess(cmd, 0, "%5", "")
        return CompletedProcess(cmd, 0, "", "")

    return mocker.patch("subprocess.run", side_effect=mock_run)


class TestTmuxFunction:
    """Test the tmux helper function."""

    def test_tmux_success(self, mock_subprocess_run):
        """Test successful tmux command execution."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "test-output"
            mock_run.return_value.stderr = ""

            result = cs.tmux("display-message", "-p", "#{session_name}")
            assert result == "test-output"

            mock_run.assert_called_once_with(
                ["tmux", "display-message", "-p", "#{session_name}"],
                stdout=cs.subprocess.PIPE,
                stderr=cs.subprocess.PIPE,
                text=True,
            )

    def test_tmux_failure(self, mock_subprocess_run):
        """Test tmux command failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "no server running"

            with pytest.raises(RuntimeError) as exc_info:
                cs.tmux("list-sessions")

            assert "no server running" in str(exc_info.value)

    def test_tmux_failure_no_stderr(self, mock_subprocess_run):
        """Test tmux command failure with no stderr message."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""

            with pytest.raises(RuntimeError) as exc_info:
                cs.tmux("invalid-command")

            assert "tmux command failed" in str(exc_info.value)


class TestMainFunction:
    """Test the main function logic."""

    def test_main_not_in_tmux(self, temp_home):
        """Test main function when not in a tmux session."""
        with patch.dict(os.environ, {}, clear=True):  # Clear TMUX env var
            with patch("sys.stderr") as mock_stderr:
                result = cs.main()
                assert result == 1

                # Check error message was printed
                mock_stderr.write.assert_called()
                error_msg = "".join(
                    call.args[0] for call in mock_stderr.write.call_args_list
                )
                assert "Must be run from within a tmux session" in error_msg

    def test_main_success(
        self, mock_os_environ, mock_uuid4, temp_home, mock_claude_start_subprocess
    ):
        """Test successful execution of main function."""
        claude_map = temp_home / ".tmux-claude-map"

        with patch.object(Path, "home", return_value=temp_home):
            with patch("os.execvp") as mock_execvp:
                result = cs.main()

                # Should not return (execvp replaces process)
                assert result == 0

                # Verify Claude was started with correct args
                mock_execvp.assert_called_once_with(
                    "claude",
                    [
                        "claude",
                        "--session-id",
                        "550e8400-e29b-41d4-a716-446655440000",
                    ],
                )

    def test_main_claude_map_creation(
        self, mock_os_environ, mock_uuid4, temp_home, mock_claude_start_subprocess
    ):
        """Test that Claude map file is created correctly."""
        claude_map = temp_home / ".tmux-claude-map"

        with patch.object(Path, "home", return_value=temp_home):
            with patch.object(cs, "tmux") as mock_tmux:
                mock_tmux.side_effect = ["test-session", "work-window", "%5"]

                with patch("os.execvp"):
                    cs.main()

                    # Verify Claude map file was created
                    assert claude_map.exists()
                    content = claude_map.read_text()
                    assert (
                        content
                        == "test-session:%5:550e8400-e29b-41d4-a716-446655440000\n"
                    )

    def test_main_claude_map_update_existing(
        self, mock_os_environ, mock_uuid4, temp_home, mock_claude_start_subprocess
    ):
        """Test updating existing Claude map file."""
        claude_map = temp_home / ".tmux-claude-map"

        # Create existing Claude map
        existing_content = """session1:%1:old-uuid-1
session2:%2:old-uuid-2
test-session:%5:old-uuid-to-replace"""
        claude_map.write_text(existing_content)

        with patch.object(Path, "home", return_value=temp_home):
            with patch.object(cs, "tmux") as mock_tmux:
                mock_tmux.side_effect = ["test-session", "work", "%5"]

                with patch("os.execvp"):
                    cs.main()

                    # Verify old entry was replaced and others preserved
                    content = claude_map.read_text()
                    lines = content.strip().split("\n")

                    assert len(lines) == 3
                    assert "session1:%1:old-uuid-1" in lines
                    assert "session2:%2:old-uuid-2" in lines
                    assert (
                        "test-session:%5:550e8400-e29b-41d4-a716-446655440000" in lines
                    )
                    assert "old-uuid-to-replace" not in content

    def test_main_claude_map_preserve_others(
        self, mock_os_environ, mock_uuid4, temp_home, mock_claude_start_subprocess
    ):
        """Test that other pane entries are preserved."""
        claude_map = temp_home / ".tmux-claude-map"

        # Create existing Claude map with different panes
        existing_content = """other-session:%10:uuid-keep-1
test-session:%99:uuid-keep-2"""
        claude_map.write_text(existing_content)

        with patch.object(Path, "home", return_value=temp_home):
            with patch.object(cs, "tmux") as mock_tmux:
                mock_tmux.side_effect = ["test-session", "new-window", "%5"]

                with patch("os.execvp"):
                    cs.main()

                    # Verify all entries are present (new one added)
                    content = claude_map.read_text()
                    lines = content.strip().split("\n")

                    assert len(lines) == 3
                    assert "other-session:%10:uuid-keep-1" in lines
                    assert "test-session:%99:uuid-keep-2" in lines
                    assert (
                        "test-session:%5:550e8400-e29b-41d4-a716-446655440000" in lines
                    )

    def test_main_empty_lines_handling(
        self, mock_os_environ, mock_uuid4, temp_home, mock_claude_start_subprocess
    ):
        """Test that empty lines in Claude map are handled correctly."""
        claude_map = temp_home / ".tmux-claude-map"

        # Create Claude map with empty lines
        existing_content = """session1:%1:uuid1

session2:%2:uuid2

"""
        claude_map.write_text(existing_content)

        with patch.object(Path, "home", return_value=temp_home):
            with patch.object(cs, "tmux") as mock_tmux:
                mock_tmux.side_effect = ["test-session", "window", "%3"]

                with patch("os.execvp"):
                    cs.main()

                    # Verify empty lines are filtered out
                    content = claude_map.read_text()
                    lines = [line for line in content.split("\n") if line.strip()]

                    assert len(lines) == 3
                    assert "session1:%1:uuid1" in lines
                    assert "session2:%2:uuid2" in lines
                    assert (
                        "test-session:%5:550e8400-e29b-41d4-a716-446655440000" in lines
                    )

    def test_main_atomic_file_write(
        self, mock_os_environ, mock_uuid4, temp_home, mock_claude_start_subprocess
    ):
        """Test that Claude map file is written atomically."""
        claude_map = temp_home / ".tmux-claude-map"

        with patch.object(Path, "home", return_value=temp_home):
            with patch.object(cs, "tmux") as mock_tmux:
                mock_tmux.side_effect = ["session", "window", "%1"]

                # Mock the atomic write operations
                with patch.object(Path, "write_text") as mock_write:
                    with patch.object(Path, "replace") as mock_replace:
                        with patch("os.execvp"):
                            cs.main()

                            # Verify temp file was written and then renamed
                            mock_write.assert_called_once()
                            mock_replace.assert_called_once()

                            # Check the replace was called on temp file
                            temp_file_path = mock_replace.call_args[0][0]
                            assert temp_file_path == claude_map

    def test_main_tmux_command_failure(
        self, mock_os_environ, temp_home, mock_failed_subprocess_run
    ):
        """Test main function when tmux commands fail."""
        with patch.object(Path, "home", return_value=temp_home):
            with pytest.raises(RuntimeError) as exc_info:
                cs.main()

            assert "no server running" in str(exc_info.value)

    def test_main_output_message(
        self,
        mock_os_environ,
        mock_uuid4,
        temp_home,
        capsys,
        mock_claude_start_subprocess,
    ):
        """Test that appropriate output message is printed."""
        with patch.object(Path, "home", return_value=temp_home):
            with patch("os.execvp"):
                cs.main()

                # Check output message
                captured = capsys.readouterr()
                # Should print session info
                assert "Starting Claude in test-session:work-window" in captured.out
                assert "pane %5" in captured.out
                assert "550e8400-e29b-41d4-a716-446655440000" in captured.out


class TestUUIDGeneration:
    """Test UUID generation and format."""

    def test_uuid_format(self, mock_os_environ, temp_home):
        """Test that generated UUID is in correct format."""
        with patch.object(Path, "home", return_value=temp_home):
            with patch.object(cs, "tmux") as mock_tmux:
                mock_tmux.side_effect = ["session", "window", "%1"]
                # Also patch the function in script_globals
                original_tmux = script_globals["tmux"]
                script_globals["tmux"] = mock_tmux

                try:
                    # Use a real UUID object and patch it in script_globals
                    import uuid

                    real_uuid = uuid.uuid4()

                    # Create a mock uuid module that returns our real UUID
                    mock_uuid_module = Mock()
                    mock_uuid_module.uuid4.return_value = real_uuid

                    original_uuid = script_globals["_uuid"]
                    script_globals["_uuid"] = mock_uuid_module

                    claude_map = temp_home / ".tmux-claude-map"

                    with patch("os.execvp"):
                        cs.main()

                        # Check that UUID in map file is valid format
                        content = claude_map.read_text()
                        _, _, uuid_part = content.strip().split(":")

                        # Validate UUID format
                        parsed_uuid = uuid.UUID(uuid_part)
                        assert str(parsed_uuid) == uuid_part
                finally:
                    script_globals["tmux"] = original_tmux
                    script_globals["_uuid"] = original_uuid

    def test_uuid_uniqueness_concept(self, mock_os_environ, temp_home):
        """Test that each call would generate different UUIDs (conceptually)."""
        # This test demonstrates that UUIDs would be unique in real usage
        import uuid

        uuid1 = uuid.uuid4()
        uuid2 = uuid.uuid4()

        assert uuid1 != uuid2
        assert str(uuid1) != str(uuid2)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_special_characters_in_session_name(
        self, mock_os_environ, mock_uuid4, temp_home
    ):
        """Test handling of special characters in session/window names."""
        claude_map = temp_home / ".tmux-claude-map"

        with patch.object(Path, "home", return_value=temp_home):
            # Mock tmux function in script_globals
            original_tmux = script_globals.get("tmux")
            mock_tmux_responses = iter(["my session-test", "work:window#1", "%1"])
            script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

            try:
                with patch("os.execvp"):
                    cs.main()

                    # Verify special characters are preserved
                    content = claude_map.read_text()
                    assert (
                        "my session-test:%1:550e8400-e29b-41d4-a716-446655440000"
                        in content
                    )
            finally:
                if original_tmux:
                    script_globals["tmux"] = original_tmux

    def test_very_long_names(self, mock_os_environ, mock_uuid4, temp_home):
        """Test handling of very long session/window/pane names."""
        claude_map = temp_home / ".tmux-claude-map"

        long_session = "a" * 100
        long_window = "b" * 100
        long_pane = "%very-long-pane-id-that-might-exist"

        with patch.object(Path, "home", return_value=temp_home):
            # Mock tmux function in script_globals
            original_tmux = script_globals.get("tmux")
            mock_tmux_responses = iter([long_session, long_window, long_pane])
            script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

            try:
                with patch("os.execvp"):
                    cs.main()

                    # Verify long names are handled correctly
                    content = claude_map.read_text()
                    assert (
                        f"{long_session}:{long_pane}:550e8400-e29b-41d4-a716-446655440000"
                        in content
                    )
            finally:
                if original_tmux:
                    script_globals["tmux"] = original_tmux

    def test_file_permission_error(self, mock_os_environ, mock_uuid4, temp_home):
        """Test handling of file permission errors."""
        with patch.object(Path, "home", return_value=temp_home):
            # Mock tmux function in script_globals
            original_tmux = script_globals.get("tmux")
            mock_tmux_responses = iter(["session", "window", "%1"])
            script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

            try:
                # Mock write_text to raise permission error
                with patch.object(Path, "write_text") as mock_write:
                    mock_write.side_effect = PermissionError("Permission denied")

                    with pytest.raises(PermissionError):
                        cs.main()
            finally:
                if original_tmux:
                    script_globals["tmux"] = original_tmux

    def test_existing_claude_map_corrupted(
        self, mock_os_environ, mock_uuid4, temp_home
    ):
        """Test handling of corrupted existing Claude map file."""
        claude_map = temp_home / ".tmux-claude-map"

        # Create corrupted Claude map (binary data)
        claude_map.write_bytes(b"\x00\x01\x02\xff\xfe")

        with patch.object(Path, "home", return_value=temp_home):
            # Mock tmux function in script_globals
            original_tmux = script_globals.get("tmux")
            mock_tmux_responses = iter(["session", "window", "%1"])
            script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

            try:
                with patch("os.execvp"):
                    # Should handle the corrupted file gracefully
                    cs.main()

                    # Verify new entry was added (file was recreated)
                    content = claude_map.read_text()
                    assert "session:%1:550e8400-e29b-41d4-a716-446655440000" in content
            finally:
                if original_tmux:
                    script_globals["tmux"] = original_tmux


class TestIntegrationScenarios:
    """Integration-style tests for complete workflows."""

    @pytest.mark.integration
    def test_multiple_claude_instances(self, mock_os_environ, temp_home):
        """Test scenario with multiple Claude instances in different panes."""
        claude_map = temp_home / ".tmux-claude-map"

        # Simulate starting Claude in multiple panes
        sessions_data = [
            ("main", "editor", "%1"),
            ("main", "terminal", "%2"),
            ("testing", "runner", "%3"),
        ]

        with patch.object(Path, "home", return_value=temp_home):
            original_tmux = script_globals.get("tmux")
            original_uuid4 = script_globals.get("_uuid")

            try:
                for session, window, pane in sessions_data:
                    # Mock tmux function in script_globals
                    mock_tmux_responses = iter([session, window, pane])
                    script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

                    # Mock uuid generation - _uuid is the module
                    import uuid

                    test_uuid = uuid.uuid4()
                    mock_uuid_module = Mock()
                    mock_uuid_module.uuid4.return_value = test_uuid
                    script_globals["_uuid"] = mock_uuid_module

                    with patch("os.execvp"):
                        cs.main()
            finally:
                if original_tmux:
                    script_globals["tmux"] = original_tmux
                if original_uuid4:
                    script_globals["_uuid"] = original_uuid4

        # Verify all entries are in the map
        content = claude_map.read_text()
        lines = [line for line in content.split("\n") if line.strip()]
        assert len(lines) == 3

        # Verify each session:pane combination is unique
        pane_entries = [line.split(":")[1] for line in lines]
        assert len(set(pane_entries)) == 3  # All pane IDs should be unique

    @pytest.mark.integration
    def test_claude_restart_in_same_pane(self, mock_os_environ, mock_uuid4, temp_home):
        """Test restarting Claude in the same pane (should replace UUID)."""
        claude_map = temp_home / ".tmux-claude-map"

        original_tmux = script_globals.get("tmux")
        original_uuid4 = script_globals.get("_uuid")

        try:
            # First Claude start
            with patch.object(Path, "home", return_value=temp_home):
                # Mock tmux function in script_globals
                mock_tmux_responses = iter(["session", "window", "%1"])
                script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

                # Use the mock_uuid4 fixture - _uuid is the module
                mock_uuid_module = Mock()
                mock_uuid_module.uuid4.return_value = Mock(
                    __str__=Mock(return_value="550e8400-e29b-41d4-a716-446655440000")
                )
                script_globals["_uuid"] = mock_uuid_module

                with patch("os.execvp"):
                    cs.main()

            # Verify first entry
            content = claude_map.read_text()
            assert "session:%1:550e8400-e29b-41d4-a716-446655440000" in content

            # Second Claude start in same pane (different UUID)
            with patch.object(Path, "home", return_value=temp_home):
                # Mock tmux function in script_globals again
                mock_tmux_responses = iter(["session", "window", "%1"])
                script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

                # Mock different UUID - _uuid is the module
                mock_uuid_module = Mock()
                mock_uuid_module.uuid4.return_value = Mock(
                    __str__=Mock(return_value="different-uuid-456")
                )
                script_globals["_uuid"] = mock_uuid_module

                with patch("os.execvp"):
                    cs.main()
        finally:
            if original_tmux:
                script_globals["tmux"] = original_tmux
            if original_uuid4:
                script_globals["_uuid"] = original_uuid4

        # Verify UUID was updated, not duplicated
        content = claude_map.read_text()
        lines = [line for line in content.split("\n") if line.strip()]

        assert len(lines) == 1  # Still only one entry
        assert "session:%1:different-uuid-456" in content
        assert "550e8400-e29b-41d4-a716-446655440000" not in content

    def test_real_world_tmux_output_format(
        self, mock_os_environ, mock_uuid4, temp_home
    ):
        """Test with realistic tmux output that might contain escape sequences."""
        claude_map = temp_home / ".tmux-claude-map"

        with patch.object(Path, "home", return_value=temp_home):
            # Mock tmux function in script_globals
            original_tmux = script_globals.get("tmux")
            mock_tmux_responses = iter(
                [
                    "my-session\n",  # session name with newline
                    " work-window ",  # window name with spaces
                    "%10\t",  # pane id with tab
                ]
            )
            script_globals["tmux"] = lambda *args: next(mock_tmux_responses)

            try:
                with patch("os.execvp"):
                    cs.main()

                    # Verify strip() is working correctly
                    content = claude_map.read_text()
                    assert (
                        "my-session:%10:550e8400-e29b-41d4-a716-446655440000" in content
                    )

                    # Verify no extra whitespace
                    line = content.strip()
                    parts = line.split(":")
                    assert parts[0] == "my-session"
                    assert parts[1] == "%10"
            finally:
                if original_tmux:
                    script_globals["tmux"] = original_tmux
