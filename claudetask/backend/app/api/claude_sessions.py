"""
API endpoints for Claude Code sessions management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
import re
from app.services.claude_sessions_reader import ClaudeSessionsReader

# Session ID validation pattern (UUID format or agent format)
# Supports: UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) or agent IDs (agent-xxxxxxxx)
SESSION_ID_PATTERN = re.compile(r'^([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}|agent-[a-f0-9]{8})$')

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
    project_dir: str = Query(None, description="Project directory path (optional, preferred)"),
    limit: int = Query(50, description="Number of sessions per page", gt=0, le=100),
    offset: int = Query(0, description="Number of sessions to skip", ge=0)
):
    """
    Get all sessions for a specific project with pagination

    Args:
        project_name: Project name (for backwards compatibility)
        project_dir: Project directory path (preferred)
        limit: Number of sessions per page (default: 50)
        offset: Number of sessions to skip (default: 0)

    Returns:
        List of sessions with metadata and pagination info
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

            # Sort by last timestamp (BEFORE pagination)
            sessions = sorted(sessions, key=lambda x: x['last_timestamp'] or "", reverse=True)

            # Apply pagination
            total = len(sessions)
            paginated_sessions = sessions[offset:offset + limit]

            return {
                "success": True,
                "project": project_name,
                "sessions": paginated_sessions,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            # Fallback to old method
            sessions = sessions_reader.get_project_sessions(project_name)

            # Apply pagination
            total = len(sessions)
            paginated_sessions = sessions[offset:offset + limit]

            return {
                "success": True,
                "project": project_name,
                "sessions": paginated_sessions,
                "total": total,
                "limit": limit,
                "offset": offset
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

        # Validate session_id format to prevent path traversal attacks
        if not SESSION_ID_PATTERN.match(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID format. Must be a valid UUID or agent ID (agent-xxxxxxxx).")

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

                            # SKIP EMPTY MESSAGES
                            if isinstance(content, str):
                                content_stripped = content.strip()
                                if not content_stripped or content_stripped in ["", "...", "…"]:
                                    continue
                            elif isinstance(content, list):
                                # For array content, check if any text blocks have actual content
                                has_content = any(
                                    block.get("text", "").strip()
                                    for block in content
                                    if isinstance(block, dict) and block.get("type") == "text"
                                )
                                if not has_content:
                                    continue
                            elif not content:
                                continue

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

                    except Exception as e:
                        logger.debug(f"Failed to parse message entry: {e}")
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
    """Get currently active Claude Code sessions - detects CLI processes running in project directories"""
    try:
        import subprocess
        import re
        from pathlib import Path

        def get_process_cwd(pid: str) -> str:
            """Get the current working directory of a process using lsof"""
            try:
                result = subprocess.run(
                    ["lsof", "-p", pid],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if '\tcwd\t' in line or ' cwd ' in line:
                        # Parse lsof output: NAME is the last column
                        parts = line.split()
                        if len(parts) >= 9:
                            # The path is everything after the 8th column
                            return ' '.join(parts[8:])
                return None
            except Exception:
                return None

        # Get list of running processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        active = []
        seen_pids = set()

        # System paths to exclude
        system_path_patterns = [
            '/var/folders/',
            '/Applications/',
            '/System/',
            '/Library/',
            '/tmp/',
            '/private/',
            '/.Trash/',
            '/Library/Caches/',
            '/usr/',
            '/opt/',
        ]

        # Patterns that indicate subprocess/helper processes (not main Claude CLI)
        exclude_patterns = [
            '--type=',           # Electron/Chrome subprocess flags
            'Helper',
            'renderer',
            'gpu-process',
            'utility',
            'crashpad',
            '/Contents/Frameworks/',
            'mcp-server',        # MCP server processes
            'resource_tracker',  # Python multiprocessing
            'spawn_main',        # Python multiprocessing
        ]

        for line in result.stdout.split('\n'):
            # Look for claude CLI processes (not Claude.app desktop app)
            # The CLI shows as "claude" or "node ...claude..." but NOT as Claude.app paths

            parts = line.split()
            if len(parts) < 11:
                continue

            pid = parts[1]
            command = ' '.join(parts[10:])
            command_lower = command.lower()

            # Skip if already processed
            if pid in seen_pids:
                continue

            # Check if this is a Claude CLI process
            is_claude_cli = False

            # Method 1: Command is exactly "claude" (the CLI binary)
            if command.strip() == 'claude' or command.startswith('claude '):
                is_claude_cli = True

            # Method 2: Has --cwd or --working-dir flag (older CLI versions)
            if '--cwd' in command or '--working-dir' in command:
                is_claude_cli = True

            if not is_claude_cli:
                continue

            # Exclude helper/subprocess patterns
            if any(pat in command for pat in exclude_patterns):
                continue

            # Get working directory
            working_dir = None

            # Try to extract from command line flags first
            if '--cwd' in command:
                match = re.search(r'--cwd[=\s]+([^\s]+)', command)
                if match:
                    working_dir = match.group(1)
            elif '--working-dir' in command:
                match = re.search(r'--working-dir[=\s]+([^\s]+)', command)
                if match:
                    working_dir = match.group(1)

            # If no flag, use lsof to get cwd
            if not working_dir:
                working_dir = get_process_cwd(pid)

            # Skip if no working directory found or it's a system path
            if not working_dir:
                continue

            if any(pat in working_dir for pat in system_path_patterns):
                continue

            seen_pids.add(pid)

            cpu = parts[2]
            mem = parts[3]
            started = parts[8]

            # Extract project name from working directory
            project_name = None
            try:
                project_name = Path(working_dir).name
            except:
                pass

            # Find the corresponding session file (most recent JSONL in project dir)
            session_id = None
            project_dir = None
            try:
                # Convert working directory to Claude projects path
                # Claude Code encodes paths by replacing / and spaces with -
                encoded_path = working_dir.replace('/', '-').replace(' ', '-')
                # Directory name starts with dash (e.g., -Users-...)
                if not encoded_path.startswith('-'):
                    encoded_path = '-' + encoded_path

                claude_projects_dir = Path.home() / '.claude' / 'projects' / encoded_path

                if claude_projects_dir.exists():
                    project_dir = str(claude_projects_dir)
                    # Find most recently modified JSONL file
                    jsonl_files = list(claude_projects_dir.glob('*.jsonl'))
                    if jsonl_files:
                        most_recent = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                        session_id = most_recent.stem  # filename without extension
            except Exception as e:
                logger.debug(f"Could not find session file: {e}")

            active.append({
                "pid": pid,
                "cpu": cpu,
                "mem": mem,
                "started": started,
                "working_dir": working_dir,
                "project_name": project_name,
                "session_id": session_id,
                "project_dir": project_dir,
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
