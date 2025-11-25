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

                            # Keep content as-is (don't convert to string if it's structured)
                            # This preserves the original structure for proper display

                            messages.append({
                                "type": entry_type,
                                "timestamp": entry.get("timestamp"),
                                "content": content,  # NO LIMIT - show full content
                                "role": "user" if entry_type == "user" else "assistant",
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
    """Get currently active Claude Code sessions - only project-related processes"""
    try:
        import subprocess
        import re

        # Get list of running claude processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        active = []
        seen_pids = set()

        for line in result.stdout.split('\n'):
            line_lower = line.lower()

            # Skip if no claude reference
            if 'claude' not in line_lower:
                continue

            # Filter for actual Claude Code project processes
            # Include: ONLY claude processes with --cwd/--working-dir pointing to user project directories
            # Exclude: ALL system subprocesses, node internals, helper processes

            is_project_session = False

            # STRICT RULE: Must have --cwd or --working-dir flag
            # This ensures we only show project-launched Claude sessions
            if '--cwd' in line or '--working-dir' in line:
                # Extract working directory
                working_dir = None
                try:
                    if '--cwd' in line:
                        match = re.search(r'--cwd[=\s]+([^\s]+)', line)
                        if match:
                            working_dir = match.group(1)
                    elif '--working-dir' in line:
                        match = re.search(r'--working-dir[=\s]+([^\s]+)', line)
                        if match:
                            working_dir = match.group(1)
                except:
                    pass

                # Verify it's a valid user project directory (not system paths)
                if working_dir:
                    # Exclude system and temporary paths
                    system_path_patterns = [
                        '/var/folders/',
                        '/Applications/',
                        '/System/',
                        '/Library/',
                        '/tmp/',
                        '/private/',
                        '/.Trash/',
                    ]
                    is_system_path = any(pat in working_dir for pat in system_path_patterns)

                    if not is_system_path:
                        is_project_session = True

            # Additional exclusions for node/electron subprocesses
            exclude_patterns = [
                '--type=',           # Electron/Chrome subprocess flags
                'helper',
                'renderer',
                'gpu-process',
                'utility',
                'crashpad',
                '/node_modules/',
                'node ',
                '/Contents/Frameworks/',
            ]
            is_excluded = any(pat in line for pat in exclude_patterns)

            if is_excluded:
                is_project_session = False

            if not is_project_session:
                continue

            # Parse process info
            parts = line.split()
            if len(parts) > 10:
                pid = parts[1]

                # Skip duplicates
                if pid in seen_pids:
                    continue
                seen_pids.add(pid)

                cpu = parts[2]
                mem = parts[3]
                started = parts[8]
                command = ' '.join(parts[10:])

                # Extract working directory
                working_dir = "Unknown"

                # Try --cwd first (newer format)
                if '--cwd' in command:
                    try:
                        match = re.search(r'--cwd[=\s]+([^\s]+)', command)
                        if match:
                            working_dir = match.group(1)
                    except:
                        pass
                # Try --working-dir (older format)
                elif '--working-dir' in command:
                    try:
                        match = re.search(r'--working-dir[=\s]+([^\s]+)', command)
                        if match:
                            working_dir = match.group(1)
                    except:
                        pass

                # Extract project name from working directory
                project_name = None
                if working_dir != "Unknown":
                    try:
                        from pathlib import Path
                        project_name = Path(working_dir).name
                    except:
                        pass

                active.append({
                    "pid": pid,
                    "cpu": cpu,
                    "mem": mem,
                    "started": started,
                    "working_dir": working_dir,
                    "project_name": project_name,
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
    Claude Code commands programmatically by launching an embedded Claude session.

    Args:
        command: Slash command to execute (e.g., /update-documentation)
        project_dir: Optional project directory path

    Returns:
        Execution status and session info
    """
    try:
        import os
        from pathlib import Path
        from app.services.real_claude_service import real_claude_service
        import uuid

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

        # Check if there's already an active session for this project
        active_session = None
        for session_id, session in real_claude_service.sessions.items():
            if session.root_project_dir == str(project_path):
                active_session = session
                logger.info(f"Found existing session {session_id} for project {project_dir}")
                break

        # If no active session, create a new one
        if not active_session:
            # Generate a unique session ID for this command execution
            session_id = f"hook-{uuid.uuid4().hex[:8]}"

            logger.info(f"Creating new Claude session {session_id} for hook command execution")

            # Create new session (uses pexpect to spawn Claude process)
            result = await real_claude_service.create_session(
                task_id=0,  # Special task ID for hook-triggered sessions
                project_path=str(project_path),
                session_id=session_id,
                root_project_path=str(project_path),
                db_session=None  # No DB tracking for hook sessions
            )

            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create Claude session: {result.get('error')}"
                )

            active_session = real_claude_service.get_session(session_id)

            # Wait a moment for Claude to initialize
            import asyncio
            await asyncio.sleep(2)
        else:
            session_id = active_session.session_id

        # Send the command to the active Claude session
        # This uses pexpect to write to Claude's stdin
        success = await real_claude_service.send_input(session_id, command)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send command to Claude session"
            )

        # Send Enter key to execute the command
        import asyncio
        await asyncio.sleep(0.2)
        await real_claude_service.send_input(session_id, "\r")

        logger.info(f"Successfully sent command '{command}' to Claude session {session_id}")

        return {
            "success": True,
            "message": f"Command {command} sent to Claude Code session",
            "command": command,
            "session_id": session_id,
            "pid": active_session.child.pid if active_session.child else None,
            "note": "Command is being executed in embedded Claude session"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_claude_command: {e}")
        raise HTTPException(status_code=500, detail=str(e))
