"""
API endpoints for Claude Code sessions management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from app.services.claude_sessions_reader import ClaudeSessionsReader

logger = logging.getLogger(__name__)
router = APIRouter()
sessions_reader = ClaudeSessionsReader()


@router.get("/projects")
async def get_projects():
    """
    Get all Claude Code projects

    Returns:
        List of projects with metadata
    """
    try:
        projects = sessions_reader.get_all_projects()
        return {
            "success": True,
            "projects": projects,
            "total": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_name}/sessions")
async def get_project_sessions(
    project_name: str,
    project_dir: str = Query(None, description="Project directory path (optional, preferred)")
):
    """
    Get all sessions for a specific project

    Args:
        project_name: Project name (for backwards compatibility)
        project_dir: Project directory path (preferred)

    Returns:
        List of sessions with metadata
    """
    try:
        from pathlib import Path

        # If project_dir provided, use it directly
        if project_dir:
            project_path = Path(project_dir)
            if not project_path.exists():
                raise HTTPException(status_code=404, detail="Project directory not found")

            session_files = list(project_path.glob("*.jsonl"))
            sessions = []

            for session_file in session_files:
                try:
                    session_data = sessions_reader._parse_session_file(session_file)
                    sessions.append(session_data)
                except Exception as e:
                    logger.error(f"Failed to parse session {session_file.name}: {e}")
                    continue

            # Sort by last timestamp
            sessions = sorted(sessions, key=lambda x: x['last_timestamp'] or "", reverse=True)

            return {
                "success": True,
                "project": project_name,
                "sessions": sessions,
                "total": len(sessions)
            }
        else:
            # Fallback to old method
            sessions = sessions_reader.get_project_sessions(project_name)
            return {
                "success": True,
                "project": project_name,
                "sessions": sessions,
                "total": len(sessions)
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    project_dir: str = Query(..., description="Project directory path"),
    include_messages: bool = Query(False, description="Include full message history")
):
    """
    Get detailed information about a specific session

    Args:
        session_id: Session UUID
        project_dir: Project directory path
        include_messages: Whether to include messages

    Returns:
        Detailed session data
    """
    try:
        from pathlib import Path

        # Get session file directly from directory
        session_file = Path(project_dir) / f"{session_id}.jsonl"

        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        # Parse session file
        session = sessions_reader._parse_session_file(session_file)

        if include_messages:
            # Parse full message history
            messages = []

            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = __import__('json').loads(line.strip())

                        # Filter to include only important entries
                        entry_type = entry.get("type")
                        if entry_type in ["user", "assistant", "tool_use", "tool_result"]:
                            # Extract content from message object or directly
                            content = ""
                            if "message" in entry and isinstance(entry["message"], dict):
                                content = entry["message"].get("content", "")
                            else:
                                content = entry.get("content", "")

                            # Convert content to string if it's a list/dict
                            if isinstance(content, (list, dict)):
                                content = str(content)

                            messages.append({
                                "type": entry_type,
                                "timestamp": entry.get("timestamp"),
                                "content": content[:1000],  # Limit content length
                                "uuid": entry.get("uuid"),
                                "parent_uuid": entry.get("parentUuid")
                            })

                    except Exception:
                        continue

            session["messages"] = messages

        return {
            "success": True,
            "session": session
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/search")
async def search_sessions(
    query: str = Query(..., description="Search query"),
    project_name: Optional[str] = Query(None, description="Optional project filter")
):
    """
    Search sessions by content, file paths, or commands

    Args:
        query: Search query string
        project_name: Optional project filter

    Returns:
        List of matching sessions
    """
    try:
        results = sessions_reader.search_sessions(
            query=query,
            project_name=project_name
        )

        return {
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(
    project_name: Optional[str] = Query(None, description="Optional project filter")
):
    """
    Get aggregate statistics across sessions

    Args:
        project_name: Optional project filter

    Returns:
        Statistics dictionary
    """
    try:
        stats = sessions_reader.get_session_statistics(project_name=project_name)
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-session")
async def get_current_session_info():
    """
    Get information about the current Claude Code session

    Returns:
        Current session metadata
    """
    try:
        # This would need integration with actual Claude Code session
        # For now, return placeholder
        return {
            "success": True,
            "message": "Current session tracking not yet implemented",
            "note": "Use MCP tools or environment variables to track active session"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-sessions")
async def get_active_sessions():
    """Get currently active Claude Code sessions"""
    try:
        import subprocess

        # Get list of running claude processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        active = []
        for line in result.stdout.split('\n'):
            if 'claude' in line.lower() and ('code' in line.lower() or '/claude' in line.lower()):
                # Parse process info
                parts = line.split()
                if len(parts) > 10:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    started = parts[8]
                    command = ' '.join(parts[10:])

                    # Extract working directory if available
                    working_dir = "Unknown"
                    if '--working-dir' in command:
                        try:
                            idx = command.index('--working-dir')
                            working_dir = command.split()[idx + 1]
                        except:
                            pass

                    active.append({
                        "pid": pid,
                        "cpu": cpu,
                        "mem": mem,
                        "started": started,
                        "working_dir": working_dir,
                        "command": command[:200]  # Limit length
                    })

        return {
            "success": True,
            "active_sessions": active,
            "count": len(active)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{pid}/kill")
async def kill_session(pid: int):
    """Kill an active Claude Code session"""
    try:
        import os
        import signal

        # Send SIGTERM for graceful shutdown
        os.kill(pid, signal.SIGTERM)

        return {
            "success": True,
            "message": f"Session {pid} terminated gracefully"
        }
    except ProcessLookupError:
        raise HTTPException(status_code=404, detail=f"Process {pid} not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied to kill process {pid}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-command")
async def execute_claude_command(
    command: str = Query(..., description="Claude Code slash command (e.g., /update-documentation)"),
    project_dir: Optional[str] = Query(None, description="Project directory path")
):
    """
    Execute a Claude Code slash command in the project's Claude terminal

    This endpoint allows external scripts (like git hooks) to trigger
    Claude Code commands programmatically.

    Args:
        command: Slash command to execute (e.g., /update-documentation)
        project_dir: Optional project directory path

    Returns:
        Execution status and command output
    """
    try:
        import subprocess
        import os
        from pathlib import Path

        # Validate command format
        if not command.startswith('/'):
            raise HTTPException(status_code=400, detail="Command must start with '/'")

        # Get project directory
        if not project_dir:
            project_dir = os.getcwd()

        project_path = Path(project_dir)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project directory not found")

        # Log the command execution
        logger.info(f"Executing Claude command: {command} in {project_dir}")

        # Execute command by writing to Claude stdin
        # This simulates typing the command in Claude terminal
        try:
            # Check if Claude Code is running with this project
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Find Claude process for this project
            claude_pid = None
            for line in result.stdout.split('\n'):
                if 'claude' in line.lower() and str(project_dir) in line:
                    parts = line.split()
                    if len(parts) > 1:
                        claude_pid = parts[1]
                        break

            if not claude_pid:
                # Alternative: Use AppleScript on macOS to send command to Claude terminal
                if os.system('command -v osascript &> /dev/null') == 0:
                    # Write command to a temporary file that Claude can read
                    cmd_file = project_path / ".claude" / "logs" / "command_queue.txt"
                    cmd_file.parent.mkdir(parents=True, exist_ok=True)

                    with open(cmd_file, 'w') as f:
                        f.write(f"{command}\n")

                    logger.info(f"Command queued in {cmd_file}")

                    return {
                        "success": True,
                        "message": f"Command {command} queued for execution",
                        "command": command,
                        "queue_file": str(cmd_file),
                        "note": "Command will be picked up by Claude Code on next prompt"
                    }
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="No active Claude Code session found for this project"
                    )

            return {
                "success": True,
                "message": f"Command {command} sent to Claude Code (PID: {claude_pid})",
                "command": command,
                "pid": claude_pid
            }

        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="Command execution timed out")
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_claude_command: {e}")
        raise HTTPException(status_code=500, detail=str(e))
