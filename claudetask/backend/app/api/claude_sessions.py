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
        from datetime import datetime
        import json as json_module

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

        def get_process_start_time(pid: str) -> datetime:
            """Get the start time of a process"""
            try:
                ps_result = subprocess.run(
                    ["ps", "-p", pid, "-o", "lstart="],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if ps_result.returncode == 0:
                    start_str = ps_result.stdout.strip()
                    return datetime.strptime(start_str, "%a %b %d %H:%M:%S %Y")
            except Exception:
                pass
            return None

        def get_session_timestamps(jsonl_file: Path) -> tuple:
            """Get first and last timestamps from a JSONL file"""
            first_ts = None
            last_ts = None
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                    for line in lines:
                        try:
                            entry = json_module.loads(line.strip())
                            ts = entry.get('timestamp')
                            if ts:
                                first_ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                break
                        except:
                            continue

                    for line in reversed(lines):
                        try:
                            entry = json_module.loads(line.strip())
                            ts = entry.get('timestamp')
                            if ts:
                                last_ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                break
                        except:
                            continue
            except Exception:
                pass
            return first_ts, last_ts

        # Get list of running processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

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

        # First pass: collect all Claude processes
        processes = []
        seen_pids = set()

        for line in result.stdout.split('\n'):
            parts = line.split()
            if len(parts) < 11:
                continue

            pid = parts[1]
            command = ' '.join(parts[10:])

            if pid in seen_pids:
                continue

            # Check if this is a Claude CLI process
            is_claude_cli = False
            if command.strip() == 'claude' or command.startswith('claude '):
                is_claude_cli = True
            if '--cwd' in command or '--working-dir' in command:
                is_claude_cli = True

            if not is_claude_cli:
                continue

            if any(pat in command for pat in exclude_patterns):
                continue

            # Get working directory
            working_dir = None
            if '--cwd' in command:
                match = re.search(r'--cwd[=\s]+([^\s]+)', command)
                if match:
                    working_dir = match.group(1)
            elif '--working-dir' in command:
                match = re.search(r'--working-dir[=\s]+([^\s]+)', command)
                if match:
                    working_dir = match.group(1)

            if not working_dir:
                working_dir = get_process_cwd(pid)

            if not working_dir:
                continue

            if any(pat in working_dir for pat in system_path_patterns):
                continue

            seen_pids.add(pid)

            # Get process start time
            process_start = get_process_start_time(pid)

            processes.append({
                "pid": pid,
                "cpu": parts[2],
                "mem": parts[3],
                "started": parts[8],
                "working_dir": working_dir,
                "project_name": Path(working_dir).name if working_dir else None,
                "command": command[:200],
                "process_start": process_start
            })

        # Second pass: for each unique project directory, match sessions to processes
        # Group processes by working directory
        from collections import defaultdict
        processes_by_dir = defaultdict(list)
        for proc in processes:
            processes_by_dir[proc['working_dir']].append(proc)

        # For each directory, get available sessions and match them to processes
        active = []
        for working_dir, dir_processes in processes_by_dir.items():
            # Convert working directory to Claude projects path
            encoded_path = working_dir.replace('/', '-').replace(' ', '-')
            if not encoded_path.startswith('-'):
                encoded_path = '-' + encoded_path

            claude_projects_dir = Path.home() / '.claude' / 'projects' / encoded_path
            project_dir = str(claude_projects_dir) if claude_projects_dir.exists() else None

            if not claude_projects_dir.exists():
                # No session files, add processes without session info
                for proc in dir_processes:
                    active.append({
                        "pid": proc["pid"],
                        "cpu": proc["cpu"],
                        "mem": proc["mem"],
                        "started": proc["started"],
                        "working_dir": working_dir,
                        "project_name": proc["project_name"],
                        "session_id": None,
                        "project_dir": None,
                        "command": proc["command"]
                    })
                continue

            # Get all session files (excluding agent files)
            jsonl_files = list(claude_projects_dir.glob('*.jsonl'))
            main_sessions = [f for f in jsonl_files if not f.stem.startswith('agent-')]

            # Collect session info
            session_info = []
            for jsonl_file in main_sessions:
                first_ts, last_ts = get_session_timestamps(jsonl_file)
                session_info.append({
                    'file': jsonl_file,
                    'session_id': jsonl_file.stem,
                    'first_ts': first_ts,
                    'last_ts': last_ts,
                    'assigned': False
                })

            # Sort sessions by last timestamp (most recent first)
            session_info.sort(
                key=lambda x: x['last_ts'].timestamp() if x['last_ts'] else 0,
                reverse=True
            )

            # Sort processes by start time (most recent first)
            dir_processes.sort(
                key=lambda x: x['process_start'].timestamp() if x['process_start'] else 0,
                reverse=True
            )

            local_tz = datetime.now().astimezone().tzinfo

            # Match processes to sessions
            for proc in dir_processes:
                session_id = None
                process_start = proc.get('process_start')

                if process_start:
                    process_start_aware = process_start.replace(tzinfo=local_tz)

                    # Try to find the best matching session for this process
                    best_match = None
                    best_score = float('inf')

                    for info in session_info:
                        if info['assigned']:
                            continue

                        if info['first_ts']:
                            # Score based on how close the session start is to process start
                            time_diff = (info['first_ts'] - process_start_aware).total_seconds()

                            # Prefer sessions that started AFTER the process (positive diff)
                            # but within reasonable time (< 30 minutes)
                            if 0 <= time_diff < 1800:  # Session started 0-30 min after process
                                score = time_diff
                            elif -300 <= time_diff < 0:  # Session started up to 5 min before process
                                score = abs(time_diff) + 100  # Penalize slightly
                            else:
                                score = abs(time_diff) + 10000  # Large penalty for far matches

                            if score < best_score:
                                best_score = score
                                best_match = info

                    if best_match and best_score < 5000:  # Only accept if reasonably close
                        session_id = best_match['session_id']
                        best_match['assigned'] = True

                # Fallback: assign most recent unassigned session
                if not session_id:
                    for info in session_info:
                        if not info['assigned']:
                            session_id = info['session_id']
                            info['assigned'] = True
                            break

                active.append({
                    "pid": proc["pid"],
                    "cpu": proc["cpu"],
                    "mem": proc["mem"],
                    "started": proc["started"],
                    "working_dir": working_dir,
                    "project_name": proc["project_name"],
                    "session_id": session_id,
                    "project_dir": project_dir,
                    "command": proc["command"]
                })

        # Also include embedded Claude sessions from real_claude_service
        try:
            from app.services.real_claude_service import real_claude_service

            embedded_sessions = real_claude_service.get_active_sessions()
            seen_session_ids = {s.get("session_id") for s in active if s.get("session_id")}

            for embedded in embedded_sessions:
                if not embedded.get("is_running"):
                    continue

                session_id = embedded.get("session_id")
                # Skip if this session is already included (matched to a CLI process)
                if session_id in seen_session_ids:
                    continue

                working_dir = embedded.get("working_dir", "")
                project_name = Path(working_dir).name if working_dir else "Unknown"

                # Get PID from the pexpect child process if available
                pid = None
                try:
                    session_obj = real_claude_service.get_session(session_id)
                    if session_obj and session_obj.child:
                        pid = str(session_obj.child.pid)
                except:
                    pass

                # Find project_dir for this session
                project_dir = None
                if working_dir:
                    encoded_path = working_dir.replace('/', '-').replace(' ', '-')
                    if not encoded_path.startswith('-'):
                        encoded_path = '-' + encoded_path
                    claude_projects_dir = Path.home() / '.claude' / 'projects' / encoded_path
                    if claude_projects_dir.exists():
                        project_dir = str(claude_projects_dir)

                active.append({
                    "pid": pid,
                    "cpu": "N/A",
                    "mem": "N/A",
                    "started": "embedded",
                    "working_dir": working_dir,
                    "project_name": project_name,
                    "session_id": session_id,
                    "project_dir": project_dir,
                    "command": "embedded claude session",
                    "task_id": embedded.get("task_id"),
                    "is_embedded": True
                })
        except Exception as e:
            logger.debug(f"Could not get embedded sessions: {e}")

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
