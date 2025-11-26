"""Unit tests for Task #15 - Session Task Details backend implementation

Tests for helper functions:
- parse_jsonl_messages: Parse Claude Code JSONL session files
- get_session_jsonl_path: Construct and validate JSONL file paths
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import parse_jsonl_messages, get_session_jsonl_path


class TestParseJsonlMessages:
    """Test suite for parse_jsonl_messages function"""

    def test_parse_jsonl_messages_valid_file(self):
        """Test parsing valid JSONL file with correct message structure"""
        # Create temporary JSONL file with valid messages
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            # Write various message formats
            messages = [
                {"type": "user", "content": "Hello", "timestamp": "2025-01-01T10:00:00Z"},
                {"type": "assistant", "content": "Hi there!", "timestamp": "2025-01-01T10:00:01Z"},
                {"type": "user", "content": "How are you?", "timestamp": "2025-01-01T10:00:02Z"},
            ]
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
            temp_path = Path(f.name)

        try:
            # Parse messages
            result = parse_jsonl_messages(temp_path)

            # Verify correct number of messages
            assert len(result) == 3

            # Verify first message structure
            assert result[0]["role"] == "user"
            assert result[0]["content"] == "Hello"
            assert result[0]["timestamp"] == "2025-01-01T10:00:00Z"

            # Verify second message
            assert result[1]["role"] == "assistant"
            assert result[1]["content"] == "Hi there!"

            # Verify third message
            assert result[2]["role"] == "user"
            assert result[2]["content"] == "How are you?"

        finally:
            # Cleanup
            temp_path.unlink()

    def test_parse_jsonl_messages_with_limit(self):
        """Test message limit works correctly"""
        # Create temporary JSONL file with multiple messages
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for i in range(10):
                msg = {
                    "type": "user",
                    "content": f"Message {i}",
                    "timestamp": f"2025-01-01T10:00:{i:02d}Z"
                }
                f.write(json.dumps(msg) + '\n')
            temp_path = Path(f.name)

        try:
            # Parse with limit of 5
            result = parse_jsonl_messages(temp_path, limit=5)

            # Verify only 5 messages returned
            assert len(result) == 5

            # Verify they are the first 5 messages
            for i in range(5):
                assert result[i]["content"] == f"Message {i}"

        finally:
            temp_path.unlink()

    def test_parse_jsonl_messages_malformed_json(self):
        """Test parsing continues and skips malformed JSON lines"""
        # Create temporary JSONL file with some malformed lines
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            # Valid message
            f.write(json.dumps({"type": "user", "content": "Message 1", "timestamp": "2025-01-01T10:00:00Z"}) + '\n')
            # Malformed JSON
            f.write('{"type": "user", "content": "incomplete\n')
            # Another valid message
            f.write(json.dumps({"type": "assistant", "content": "Message 2", "timestamp": "2025-01-01T10:00:01Z"}) + '\n')
            # Invalid JSON syntax
            f.write('not json at all\n')
            # Another valid message
            f.write(json.dumps({"type": "user", "content": "Message 3", "timestamp": "2025-01-01T10:00:02Z"}) + '\n')
            temp_path = Path(f.name)

        try:
            # Parse messages (should skip malformed lines)
            result = parse_jsonl_messages(temp_path)

            # Verify only valid messages are returned
            assert len(result) == 3
            assert result[0]["content"] == "Message 1"
            assert result[1]["content"] == "Message 2"
            assert result[2]["content"] == "Message 3"

        finally:
            temp_path.unlink()

    def test_parse_jsonl_messages_empty_file(self):
        """Test parsing empty file returns empty list"""
        # Create empty temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Parse empty file
            result = parse_jsonl_messages(temp_path)

            # Verify empty list returned
            assert result == []

        finally:
            temp_path.unlink()

    def test_parse_jsonl_messages_nested_content(self):
        """Test messages with nested content format are handled correctly"""
        # Create temporary JSONL file with nested message format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            messages = [
                # Nested content format (message.content)
                {"type": "user", "message": {"content": "Nested user message"}, "timestamp": "2025-01-01T10:00:00Z"},
                {"type": "assistant", "message": {"content": "Nested assistant message"}, "timestamp": "2025-01-01T10:00:01Z"},
                # Direct content format
                {"type": "user", "content": "Direct user message", "timestamp": "2025-01-01T10:00:02Z"},
            ]
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
            temp_path = Path(f.name)

        try:
            # Parse messages
            result = parse_jsonl_messages(temp_path)

            # Verify correct extraction of nested content
            assert len(result) == 3
            assert result[0]["content"] == "Nested user message"
            assert result[1]["content"] == "Nested assistant message"
            assert result[2]["content"] == "Direct user message"

        finally:
            temp_path.unlink()

    def test_parse_jsonl_messages_filters_non_user_assistant_types(self):
        """Test that only user and assistant type messages are included"""
        # Create temporary JSONL file with various message types
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            messages = [
                {"type": "user", "content": "User message", "timestamp": "2025-01-01T10:00:00Z"},
                {"type": "system", "content": "System message", "timestamp": "2025-01-01T10:00:01Z"},
                {"type": "assistant", "content": "Assistant message", "timestamp": "2025-01-01T10:00:02Z"},
                {"type": "metadata", "content": "Metadata", "timestamp": "2025-01-01T10:00:03Z"},
                {"type": "user", "content": "Another user message", "timestamp": "2025-01-01T10:00:04Z"},
            ]
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
            temp_path = Path(f.name)

        try:
            # Parse messages
            result = parse_jsonl_messages(temp_path)

            # Verify only user and assistant messages are included
            assert len(result) == 3
            assert result[0]["role"] == "user"
            assert result[1]["role"] == "assistant"
            assert result[2]["role"] == "user"

        finally:
            temp_path.unlink()

    def test_parse_jsonl_messages_missing_timestamp(self):
        """Test messages without timestamp are handled gracefully"""
        # Create temporary JSONL file with messages missing timestamp
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            messages = [
                {"type": "user", "content": "Message without timestamp"},
                {"type": "assistant", "content": "Another message", "timestamp": "2025-01-01T10:00:01Z"},
            ]
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
            temp_path = Path(f.name)

        try:
            # Parse messages
            result = parse_jsonl_messages(temp_path)

            # Verify messages are parsed (timestamp is optional)
            assert len(result) == 2
            assert result[0]["timestamp"] is None
            assert result[1]["timestamp"] == "2025-01-01T10:00:01Z"

        finally:
            temp_path.unlink()

    def test_parse_jsonl_messages_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises appropriate error"""
        nonexistent_path = Path("/nonexistent/path/to/file.jsonl")

        # Should raise FileNotFoundError or similar
        with pytest.raises(Exception):
            parse_jsonl_messages(nonexistent_path)


class TestGetSessionJsonlPath:
    """Test suite for get_session_jsonl_path function"""

    def test_get_session_jsonl_path_valid(self):
        """Test path construction with valid project_id and session_id"""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock Path.home() to return temp directory
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create .claude/projects directory structure
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                project_dir = claude_dir / "test-project"
                project_dir.mkdir(parents=True)

                # Create a test JSONL file
                session_id = "session-123"
                jsonl_file = project_dir / f"{session_id}.jsonl"
                jsonl_file.write_text('{"type": "user", "content": "test"}')

                # Test path construction
                result = get_session_jsonl_path("test/project", session_id)

                # Verify correct path is returned
                assert result is not None
                assert result.exists()
                assert result.name == f"{session_id}.jsonl"

    def test_get_session_jsonl_path_with_slashes(self):
        """Test path encoding when project_id contains slashes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create directory with encoded slashes
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                # Slashes should be replaced with dashes
                project_dir = claude_dir / "user-projects-myproject"
                project_dir.mkdir(parents=True)

                session_id = "session-456"
                jsonl_file = project_dir / f"{session_id}.jsonl"
                jsonl_file.write_text('{"type": "user", "content": "test"}')

                # Test with project_id containing slashes
                result = get_session_jsonl_path("user/projects/myproject", session_id)

                # Verify path is found
                assert result is not None
                assert result.exists()

    def test_get_session_jsonl_path_nonexistent(self):
        """Test returns None for non-existent session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create .claude/projects directory but no session file
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                project_dir = claude_dir / "test-project"
                project_dir.mkdir(parents=True)

                # Test with non-existent session
                result = get_session_jsonl_path("test/project", "nonexistent-session")

                # Verify None is returned
                assert result is None

    def test_get_session_jsonl_path_security_path_traversal(self):
        """Test that path traversal attempts are blocked"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create .claude directory
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                claude_dir.mkdir(parents=True)

                # Create a file outside .claude directory
                outside_dir = Path(tmpdir) / "outside"
                outside_dir.mkdir()
                outside_file = outside_dir / "session.jsonl"
                outside_file.write_text('{"type": "user", "content": "test"}')

                # Attempt path traversal
                result = get_session_jsonl_path("../../../outside", "session")

                # Should return None (security check)
                assert result is None

    def test_get_session_jsonl_path_security_absolute_path(self):
        """Test that absolute paths outside .claude are blocked"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create .claude directory
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                claude_dir.mkdir(parents=True)

                # Try to access /etc/passwd or similar
                result = get_session_jsonl_path("/etc", "passwd")

                # Should return None (security check or file doesn't exist)
                assert result is None

    def test_get_session_jsonl_path_symlink_outside_claude(self):
        """Test that symlinks pointing outside .claude are blocked"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create .claude directory
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                project_dir = claude_dir / "test-project"
                project_dir.mkdir(parents=True)

                # Create a file outside .claude
                outside_dir = Path(tmpdir) / "outside"
                outside_dir.mkdir()
                outside_file = outside_dir / "secret.jsonl"
                outside_file.write_text('{"type": "user", "content": "secret"}')

                # Create symlink inside project pointing outside
                symlink_file = project_dir / "session.jsonl"
                try:
                    symlink_file.symlink_to(outside_file)
                except OSError:
                    # Skip test if symlinks not supported (e.g., Windows without admin)
                    pytest.skip("Symlinks not supported on this system")

                # Test with symlinked file
                result = get_session_jsonl_path("test/project", "session")

                # Should return None (security check blocks symlink to outside)
                assert result is None

    def test_get_session_jsonl_path_encoding_special_chars(self):
        """Test project_id with special characters is encoded correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Create directory with encoded special chars
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                # Forward slashes replaced with dashes
                project_dir = claude_dir / "my-project-v2"
                project_dir.mkdir(parents=True)

                session_id = "session-789"
                jsonl_file = project_dir / f"{session_id}.jsonl"
                jsonl_file.write_text('{"type": "user", "content": "test"}')

                # Test with special characters
                result = get_session_jsonl_path("my/project/v2", session_id)

                # Verify path is found
                assert result is not None
                assert result.exists()


class TestIntegration:
    """Integration tests combining both functions"""

    def test_parse_messages_from_constructed_path(self):
        """Test full workflow: construct path and parse messages"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)

                # Setup directory structure
                claude_dir = Path(tmpdir) / ".claude" / "projects"
                project_dir = claude_dir / "integration-test"
                project_dir.mkdir(parents=True)

                # Create JSONL file with test messages
                session_id = "integration-session"
                jsonl_file = project_dir / f"{session_id}.jsonl"
                messages = [
                    {"type": "user", "content": "Start conversation", "timestamp": "2025-01-01T10:00:00Z"},
                    {"type": "assistant", "message": {"content": "Hello! How can I help?"}, "timestamp": "2025-01-01T10:00:01Z"},
                    {"type": "user", "content": "Thanks!", "timestamp": "2025-01-01T10:00:02Z"},
                ]
                with jsonl_file.open('w') as f:
                    for msg in messages:
                        f.write(json.dumps(msg) + '\n')

                # Get path using function
                path = get_session_jsonl_path("integration/test", session_id)
                assert path is not None

                # Parse messages from constructed path
                parsed = parse_jsonl_messages(path)

                # Verify complete workflow
                assert len(parsed) == 3
                assert parsed[0]["content"] == "Start conversation"
                assert parsed[1]["content"] == "Hello! How can I help?"
                assert parsed[2]["content"] == "Thanks!"
