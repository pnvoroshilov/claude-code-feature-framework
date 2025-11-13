"""
Claude Code Sessions Reader Service
Reads and parses Claude Code session data from ~/.claude/projects/
Similar to Claudia's approach
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ClaudeSessionsReader:
    """Service for reading Claude Code sessions from local storage"""

    def __init__(self):
        self.claude_projects_dir = Path.home() / ".claude" / "projects"

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Get all Claude Code projects

        Returns:
            List of projects with metadata
        """
        projects = []

        if not self.claude_projects_dir.exists():
            logger.warning(f"Claude projects directory not found: {self.claude_projects_dir}")
            return projects

        for project_dir in self.claude_projects_dir.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                # Parse project name from directory (Claude encodes paths with dashes)
                project_path = project_dir.name.replace('-', '/')

                # Extract meaningful project name from the actual project path
                # Remove leading slash and split by /
                path_parts = [p for p in project_path.split('/') if p]

                # Find "Desktop/Work/Start/Up/" and get everything after it
                if 'Up' in path_parts:
                    try:
                        up_index = path_parts.index('Up')
                        # Get everything after "Up" as the project name
                        project_name_parts = path_parts[up_index + 1:]
                        display_name = ' '.join(project_name_parts) if project_name_parts else path_parts[-1]
                    except (ValueError, IndexError):
                        # Fallback to last segment
                        display_name = path_parts[-1] if path_parts else project_dir.name
                else:
                    # Fallback to last segment
                    display_name = path_parts[-1] if path_parts else project_dir.name

                # Get sessions count
                session_files = list(project_dir.glob("*.jsonl"))

                projects.append({
                    "name": display_name,
                    "path": project_path,
                    "directory": str(project_dir),
                    "sessions_count": len(session_files),
                    "last_modified": datetime.fromtimestamp(
                        project_dir.stat().st_mtime
                    ).isoformat()
                })

        return sorted(projects, key=lambda x: x['last_modified'], reverse=True)

    def get_project_sessions(self, project_name: str) -> List[Dict[str, Any]]:
        """
        Get all sessions for a specific project

        Args:
            project_name: Project directory name (e.g., "Claude-Code-Feature-Framework")

        Returns:
            List of sessions with metadata
        """
        sessions = []

        # Find project directory
        project_dirs = [d for d in self.claude_projects_dir.iterdir()
                       if d.is_dir() and project_name.lower() in d.name.lower()]

        if not project_dirs:
            logger.warning(f"Project not found: {project_name}")
            return sessions

        project_dir = project_dirs[0]

        for session_file in project_dir.glob("*.jsonl"):
            try:
                session_data = self._parse_session_file(session_file)
                sessions.append(session_data)
            except Exception as e:
                logger.error(f"Failed to parse session {session_file.name}: {e}")
                continue

        return sorted(sessions, key=lambda x: x['last_timestamp'], reverse=True)

    def _parse_session_file(self, session_file: Path) -> Dict[str, Any]:
        """
        Parse a single session JSONL file

        Args:
            session_file: Path to session JSONL file

        Returns:
            Session metadata and statistics
        """
        session_id = session_file.stem

        # Session metadata
        metadata = {
            "session_id": session_id,
            "file_path": str(session_file),
            "file_size": session_file.stat().st_size,
            "created_at": None,
            "last_timestamp": None,
            "cwd": None,
            "git_branch": None,
            "claude_version": None,
            "message_count": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "tool_calls": defaultdict(int),
            "commands_used": [],
            "files_modified": [],
            "errors": []
        }

        first_timestamp = None
        last_timestamp = None

        # Parse JSONL file line by line
        with open(session_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())

                    # Extract metadata from first entry
                    if line_num == 1:
                        metadata["cwd"] = entry.get("cwd")
                        metadata["git_branch"] = entry.get("gitBranch")
                        metadata["claude_version"] = entry.get("version")
                        first_timestamp = entry.get("timestamp")

                    # Track timestamps
                    timestamp = entry.get("timestamp")
                    if timestamp:
                        last_timestamp = timestamp

                    # Count message types
                    entry_type = entry.get("type")
                    subtype = entry.get("subtype")

                    if entry_type == "user":
                        metadata["user_messages"] += 1
                        metadata["message_count"] += 1
                    elif entry_type == "assistant":
                        metadata["assistant_messages"] += 1
                        metadata["message_count"] += 1

                    # Track tool calls
                    if entry_type == "tool_use":
                        tool_name = entry.get("name", "unknown")
                        metadata["tool_calls"][tool_name] += 1

                    # Track commands
                    if subtype == "local_command":
                        content = entry.get("content", "")
                        if "<command-name>" in content:
                            command = content.split("<command-name>")[1].split("</command-name>")[0]
                            if command not in metadata["commands_used"]:
                                metadata["commands_used"].append(command)

                    # Track file modifications
                    if entry_type == "tool_result":
                        tool_name = entry.get("name")
                        if tool_name in ["Write", "Edit", "MultiEdit"]:
                            # Extract file path from tool parameters
                            params = entry.get("parameters", {})
                            file_path = params.get("file_path")
                            if file_path and file_path not in metadata["files_modified"]:
                                metadata["files_modified"].append(file_path)

                    # Track errors
                    if entry.get("level") == "error" or entry_type == "error":
                        metadata["errors"].append({
                            "timestamp": timestamp,
                            "content": entry.get("content", "Unknown error")[:200]
                        })

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON at line {line_num} in {session_file.name}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error parsing line {line_num} in {session_file.name}: {e}")
                    continue

        # Set timestamps
        metadata["created_at"] = first_timestamp
        metadata["last_timestamp"] = last_timestamp

        # Convert defaultdict to regular dict
        metadata["tool_calls"] = dict(metadata["tool_calls"])

        return metadata

    def get_session_details(
        self,
        project_name: str,
        session_id: str,
        include_messages: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific session

        Args:
            project_name: Project directory name
            session_id: Session UUID
            include_messages: Whether to include full message history

        Returns:
            Detailed session data or None if not found
        """
        # Find project directory
        project_dirs = [d for d in self.claude_projects_dir.iterdir()
                       if d.is_dir() and project_name.lower() in d.name.lower()]

        if not project_dirs:
            return None

        project_dir = project_dirs[0]
        session_file = project_dir / f"{session_id}.jsonl"

        if not session_file.exists():
            return None

        # Get basic metadata
        session_data = self._parse_session_file(session_file)

        if include_messages:
            # Parse full message history
            messages = []

            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())

                        # Filter to include only important entries
                        entry_type = entry.get("type")
                        if entry_type in ["user", "assistant", "tool_use", "tool_result"]:
                            messages.append({
                                "type": entry_type,
                                "timestamp": entry.get("timestamp"),
                                "content": entry.get("content", "")[:500],  # Limit content length
                                "uuid": entry.get("uuid"),
                                "parent_uuid": entry.get("parentUuid")
                            })

                    except Exception as e:
                        continue

            session_data["messages"] = messages

        return session_data

    def search_sessions(
        self,
        query: str,
        project_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search sessions by content, file paths, or commands

        Args:
            query: Search query string
            project_name: Optional project filter

        Returns:
            List of matching sessions
        """
        results = []

        # Get projects to search
        if project_name:
            project_dirs = [d for d in self.claude_projects_dir.iterdir()
                           if d.is_dir() and project_name.lower() in d.name.lower()]
        else:
            project_dirs = [d for d in self.claude_projects_dir.iterdir()
                           if d.is_dir() and not d.name.startswith('.')]

        query_lower = query.lower()

        for project_dir in project_dirs:
            for session_file in project_dir.glob("*.jsonl"):
                try:
                    # Quick search in file content
                    with open(session_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                        if query_lower in content.lower():
                            session_data = self._parse_session_file(session_file)
                            session_data["project"] = project_dir.name
                            results.append(session_data)

                except Exception as e:
                    logger.error(f"Error searching session {session_file.name}: {e}")
                    continue

        return sorted(results, key=lambda x: x['last_timestamp'], reverse=True)

    def get_session_statistics(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregate statistics across sessions

        Args:
            project_name: Optional project filter

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_sessions": 0,
            "total_messages": 0,
            "total_tool_calls": defaultdict(int),
            "most_active_project": None,
            "recent_sessions": [],
            "total_files_modified": set(),
            "total_errors": 0
        }

        sessions = []

        if project_name:
            sessions = self.get_project_sessions(project_name)
        else:
            projects = self.get_all_projects()
            for project in projects:
                project_sessions = self.get_project_sessions(project["name"])
                sessions.extend(project_sessions)

        # Aggregate statistics
        for session in sessions:
            stats["total_sessions"] += 1
            stats["total_messages"] += session["message_count"]
            stats["total_errors"] += len(session["errors"])

            # Aggregate tool calls
            for tool, count in session["tool_calls"].items():
                stats["total_tool_calls"][tool] += count

            # Track file modifications
            for file_path in session["files_modified"]:
                stats["total_files_modified"].add(file_path)

        # Convert sets to lists and defaultdict to dict
        stats["total_files_modified"] = len(stats["total_files_modified"])
        stats["total_tool_calls"] = dict(stats["total_tool_calls"])

        # Get most recent sessions
        stats["recent_sessions"] = sorted(
            sessions,
            key=lambda x: x['last_timestamp'] or "",
            reverse=True
        )[:10]

        return stats
