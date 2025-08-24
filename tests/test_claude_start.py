"""Tests for claude-start command."""

from unittest.mock import patch

import pytest

from cli.app.command.tmux.claude import claude_start


@pytest.fixture
def patch_claude_map_file(temp_home):
    """Patch CLAUDE_MAP_FILE to use temp directory."""
    temp_claude_map = temp_home / ".tmux-claude-map"
    with patch("cli.app.command.tmux.claude.CLAUDE_MAP_FILE", temp_claude_map):
        yield temp_claude_map


@pytest.fixture
def mock_tmux_display_commands(mocker):
    """Mock tmux display-message commands for claude-start."""

    def tmux_side_effect(*args):
        if "#{session_name}" in " ".join(args):
            return "main-session\n"
        elif "#{window_name}" in " ".join(args):
            return "editor\n"
        elif "#{pane_id}" in " ".join(args):
            return "%1\n"
        return ""

    return mocker.patch(
        "cli.app.command.tmux.claude.tmux", side_effect=tmux_side_effect
    )


class TestClaudeStartCommand:
    """Test claude-start command functionality."""

    def test_claude_start_not_in_tmux(self):
        """Test claude-start when not in tmux session."""
        from click.testing import CliRunner

        runner = CliRunner()
        with patch.dict("os.environ", {}, clear=True):  # No TMUX env var
            result = runner.invoke(claude_start)
            assert result.exit_code == 1
            assert "Must be run from within a tmux session" in result.output

    def test_claude_start_success(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test successful claude-start execution."""
        from click.testing import CliRunner

        runner = CliRunner()

        # Mock os.execvp to prevent actual claude execution
        with patch("cli.app.command.tmux.claude.os.execvp") as mock_execvp:
            result = runner.invoke(claude_start)

            # Check that execvp was called correctly
            mock_execvp.assert_called_once_with(
                "claude",
                ["claude", "--session-id", "550e8400-e29b-41d4-a716-446655440000"],
            )

            # Check that the mapping was written
            content = patch_claude_map_file.read_text()
            expected_line = "main-session:%1:550e8400-e29b-41d4-a716-446655440000"
            assert expected_line in content

    def test_claude_start_replaces_existing_mapping(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test that claude-start replaces existing mapping for same pane."""
        from click.testing import CliRunner

        # Set up existing mapping
        existing_content = """main-session:%1:old-uuid-that-should-be-replaced
other-session:%2:other-uuid-that-should-remain"""
        patch_claude_map_file.write_text(existing_content)

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            result = runner.invoke(claude_start)

            content = patch_claude_map_file.read_text()
            lines = content.strip().split("\n")

            # Should have 2 lines: one replaced, one preserved
            assert len(lines) == 2
            assert "main-session:%1:550e8400-e29b-41d4-a716-446655440000" in content
            assert "other-session:%2:other-uuid-that-should-remain" in content
            assert "old-uuid-that-should-be-replaced" not in content

    def test_claude_start_preserves_other_mappings(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test that claude-start preserves other pane mappings."""
        from click.testing import CliRunner

        existing_content = """other-session:%2:uuid-1
another-session:%3:uuid-2
third-session:%4:uuid-3"""
        patch_claude_map_file.write_text(existing_content)

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            result = runner.invoke(claude_start)

            content = patch_claude_map_file.read_text()
            lines = [line for line in content.strip().split("\n") if line.strip()]

            # Should have 4 lines: 3 existing + 1 new
            assert len(lines) == 4
            assert "other-session:%2:uuid-1" in content
            assert "another-session:%3:uuid-2" in content
            assert "third-session:%4:uuid-3" in content
            assert "main-session:%1:550e8400-e29b-41d4-a716-446655440000" in content

    def test_claude_start_handles_corrupted_map_file(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test claude-start with corrupted existing map file."""
        from click.testing import CliRunner

        # Write binary/corrupted content that will cause UnicodeDecodeError
        patch_claude_map_file.write_bytes(b"\xff\xfe\x00\x01corrupted")

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            result = runner.invoke(claude_start)

            # Should handle gracefully and create new mapping
            content = patch_claude_map_file.read_text()
            assert "main-session:%1:550e8400-e29b-41d4-a716-446655440000" in content

            # Should only have the new line (corrupted content discarded)
            lines = [line for line in content.strip().split("\n") if line.strip()]
            assert len(lines) == 1

    def test_claude_start_handles_empty_lines_in_map(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test claude-start handles empty lines in map file correctly."""
        from click.testing import CliRunner

        existing_content = """
        
main-session:%2:existing-uuid

other-session:%3:another-uuid

"""
        patch_claude_map_file.write_text(existing_content)

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            result = runner.invoke(claude_start)

            content = patch_claude_map_file.read_text()
            lines = [line for line in content.strip().split("\n") if line.strip()]

            # Should preserve non-empty lines and add new one
            assert len(lines) == 3
            assert "main-session:%2:existing-uuid" in content
            assert "other-session:%3:another-uuid" in content
            assert "main-session:%1:550e8400-e29b-41d4-a716-446655440000" in content

    def test_claude_start_tmux_command_failure(
        self, mock_os_environ, mock_uuid4, patch_claude_map_file
    ):
        """Test claude-start when tmux commands fail."""
        from click.testing import CliRunner

        # Mock tmux to raise RuntimeError
        with patch(
            "cli.app.command.tmux.claude.tmux", side_effect=RuntimeError("tmux failed")
        ):
            runner = CliRunner()
            result = runner.invoke(claude_start)

            assert result.exit_code == 1
            assert "Error getting tmux info" in result.output

    def test_claude_start_claude_not_found(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test claude-start when claude command not found."""
        from click.testing import CliRunner

        runner = CliRunner()

        # Mock os.execvp to raise FileNotFoundError
        with patch(
            "cli.app.command.tmux.claude.os.execvp",
            side_effect=FileNotFoundError("claude not found"),
        ):
            result = runner.invoke(claude_start)

            assert result.exit_code == 1
            assert "claude command not found" in result.output

    def test_claude_start_output_format(
        self,
        mock_os_environ,
        mock_tmux_display_commands,
        mock_uuid4,
        patch_claude_map_file,
    ):
        """Test claude-start output message format."""
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            result = runner.invoke(claude_start)

            expected_output = "Starting Claude in main-session:editor (pane %1) with session ID: 550e8400-e29b-41d4-a716-446655440000"
            assert expected_output in result.output

    def test_claude_start_uuid_generation_and_format(
        self, mock_os_environ, mock_tmux_display_commands, patch_claude_map_file
    ):
        """Test that claude-start generates valid UUIDs."""
        from click.testing import CliRunner
        import uuid as _uuid

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            # Don't mock uuid4 - use real UUID generation
            result = runner.invoke(claude_start)

            content = patch_claude_map_file.read_text()
            lines = [line for line in content.strip().split("\n") if line.strip()]
            assert len(lines) == 1

            # Extract the UUID from the line
            parts = lines[0].split(":")
            assert len(parts) == 3
            generated_uuid = parts[2]

            # Verify it's a valid UUID format
            try:
                uuid_obj = _uuid.UUID(generated_uuid)
                assert str(uuid_obj) == generated_uuid
            except ValueError:
                pytest.fail(f"Generated UUID '{generated_uuid}' is not valid")

    def test_claude_start_with_special_characters_in_names(
        self, mock_os_environ, mock_uuid4, patch_claude_map_file
    ):
        """Test claude-start with special characters in session/window names."""
        from click.testing import CliRunner

        def tmux_side_effect(*args):
            if "#{session_name}" in " ".join(args):
                return "my-special:session@name\n"
            elif "#{window_name}" in " ".join(args):
                return "editor (project-1)\n"
            elif "#{pane_id}" in " ".join(args):
                return "%1\n"
            return ""

        with patch("cli.app.command.tmux.claude.tmux", side_effect=tmux_side_effect):
            runner = CliRunner()

            with patch("cli.app.command.tmux.claude.os.execvp"):
                result = runner.invoke(claude_start)

                content = patch_claude_map_file.read_text()
                expected_line = (
                    "my-special:session@name:%1:550e8400-e29b-41d4-a716-446655440000"
                )
                assert expected_line in content

                # Output should show the special characters correctly
                assert "my-special:session@name:editor (project-1)" in result.output

    def test_claude_start_with_very_long_names(
        self, mock_os_environ, mock_uuid4, patch_claude_map_file
    ):
        """Test claude-start with very long session/window names."""
        from click.testing import CliRunner

        long_session = "a" * 100
        long_window = "b" * 100

        def tmux_side_effect(*args):
            if "#{session_name}" in " ".join(args):
                return f"{long_session}\n"
            elif "#{window_name}" in " ".join(args):
                return f"{long_window}\n"
            elif "#{pane_id}" in " ".join(args):
                return "%1\n"
            return ""

        with patch("cli.app.command.tmux.claude.tmux", side_effect=tmux_side_effect):
            runner = CliRunner()

            with patch("cli.app.command.tmux.claude.os.execvp"):
                result = runner.invoke(claude_start)

                content = patch_claude_map_file.read_text()
                expected_line = (
                    f"{long_session}:%1:550e8400-e29b-41d4-a716-446655440000"
                )
                assert expected_line in content

                # Output should show the long names
                assert long_session in result.output
                assert long_window in result.output

    def test_real_uuid_uniqueness_across_multiple_calls(
        self, mock_os_environ, mock_tmux_display_commands, patch_claude_map_file
    ):
        """Test that multiple claude-start calls generate unique UUIDs."""
        from click.testing import CliRunner
        import uuid as _uuid

        runner = CliRunner()
        generated_uuids = set()

        # Run claude-start multiple times and collect UUIDs
        for i in range(5):

            def tmux_side_effect(*args):
                if "#{session_name}" in " ".join(args):
                    return f"session-{i}\n"
                elif "#{window_name}" in " ".join(args):
                    return "editor\n"
                elif "#{pane_id}" in " ".join(args):
                    return f"%{i + 1}\n"
                return ""

            with patch(
                "cli.app.command.tmux.claude.tmux", side_effect=tmux_side_effect
            ):
                with patch("cli.app.command.tmux.claude.os.execvp"):
                    result = runner.invoke(claude_start)
                    assert result.exit_code == 0

        # Parse all generated UUIDs from the map file
        content = patch_claude_map_file.read_text()
        lines = [line for line in content.strip().split("\n") if line.strip()]

        for line in lines:
            parts = line.split(":")
            assert len(parts) == 3
            uuid_str = parts[2]

            # Verify it's a valid UUID
            try:
                uuid_obj = _uuid.UUID(uuid_str)
                assert str(uuid_obj) == uuid_str
                generated_uuids.add(uuid_str)
            except ValueError:
                pytest.fail(f"Generated UUID '{uuid_str}' is not valid")

        # All UUIDs should be unique
        assert len(generated_uuids) == 5

    def test_real_uuid_version_and_format(
        self, mock_os_environ, mock_tmux_display_commands, patch_claude_map_file
    ):
        """Test that generated UUIDs are version 4 and properly formatted."""
        from click.testing import CliRunner
        import uuid as _uuid
        import re

        runner = CliRunner()

        with patch("cli.app.command.tmux.claude.os.execvp"):
            result = runner.invoke(claude_start)
            assert result.exit_code == 0

        content = patch_claude_map_file.read_text()
        lines = [line for line in content.strip().split("\n") if line.strip()]
        assert len(lines) == 1

        parts = lines[0].split(":")
        uuid_str = parts[2]

        # Verify UUID format with regex
        uuid_pattern = (
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
        assert re.match(uuid_pattern, uuid_str, re.IGNORECASE), (
            f"UUID {uuid_str} doesn't match expected format"
        )

        # Verify it's version 4
        uuid_obj = _uuid.UUID(uuid_str)
        assert uuid_obj.version == 4, (
            f"Expected version 4 UUID, got version {uuid_obj.version}"
        )

    def test_uuid_persistence_across_sessions(
        self, mock_os_environ, mock_tmux_display_commands, patch_claude_map_file
    ):
        """Test that UUIDs are properly persisted and not regenerated on subsequent calls."""
        from click.testing import CliRunner

        runner = CliRunner()

        # First invocation - generate UUID
        with patch("cli.app.command.tmux.claude.os.execvp"):
            result1 = runner.invoke(claude_start)
            assert result1.exit_code == 0

        content1 = patch_claude_map_file.read_text()
        first_uuid = content1.strip().split(":")[2]

        # Second invocation with same pane - should replace with new UUID
        with patch("cli.app.command.tmux.claude.os.execvp"):
            result2 = runner.invoke(claude_start)
            assert result2.exit_code == 0

        content2 = patch_claude_map_file.read_text()
        second_uuid = content2.strip().split(":")[2]

        # Should be different UUIDs since we're starting a new session for same pane
        assert first_uuid != second_uuid

        # Verify both are valid UUIDs
        import uuid as _uuid

        _uuid.UUID(first_uuid)
        _uuid.UUID(second_uuid)

    def test_uuid_handling_with_concurrent_panes(
        self, mock_os_environ, patch_claude_map_file
    ):
        """Test UUID generation for multiple panes in different sessions."""
        from click.testing import CliRunner
        import uuid as _uuid

        runner = CliRunner()

        # Simulate starting Claude in multiple different panes
        pane_configs = [
            ("session1", "window1", "%1"),
            ("session1", "window2", "%2"),
            ("session2", "window1", "%3"),
            ("session2", "window2", "%4"),
        ]

        for session, window, pane_id in pane_configs:

            def tmux_side_effect(*args):
                if "#{session_name}" in " ".join(args):
                    return f"{session}\n"
                elif "#{window_name}" in " ".join(args):
                    return f"{window}\n"
                elif "#{pane_id}" in " ".join(args):
                    return f"{pane_id}\n"
                return ""

            with patch(
                "cli.app.command.tmux.claude.tmux", side_effect=tmux_side_effect
            ):
                with patch("cli.app.command.tmux.claude.os.execvp"):
                    result = runner.invoke(claude_start)
                    assert result.exit_code == 0

        # Verify all UUIDs are unique and valid
        content = patch_claude_map_file.read_text()
        lines = [line for line in content.strip().split("\n") if line.strip()]

        assert len(lines) == 4

        uuids = []
        for line in lines:
            parts = line.split(":")
            assert len(parts) == 3
            session_pane = f"{parts[0]}:{parts[1]}"
            uuid_str = parts[2]

            # Verify UUID is valid
            uuid_obj = _uuid.UUID(uuid_str)
            assert str(uuid_obj) == uuid_str
            uuids.append(uuid_str)

        # All UUIDs should be unique
        assert len(set(uuids)) == 4
