"""MCP & Hooks Logs Router - API endpoints for viewing MCP call logs and Hook execution logs

Logs are stored per-project in:
- MCP: {project_path}/.claudetask/logs/mcp/mcp_calls.log
- Hooks: {project_path}/.claudetask/logs/hooks/hooks.log
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import json
import asyncio
import re

from ..database import get_db
from ..models import Project

router = APIRouter(prefix="/api/mcp-logs", tags=["mcp-logs"])


def get_log_file_for_project(project_path: str) -> Path:
    """Get the log file path for a specific project"""
    return Path(project_path) / ".claudetask" / "logs" / "mcp" / "mcp_calls.log"


def parse_log_line(line: str) -> Optional[dict]:
    """Parse a single log line into a structured format"""
    # Pattern: 2025-11-24 20:30:15,123 - __main__ - INFO - message
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\w+) - (.+)$'
    match = re.match(pattern, line.strip())

    if match:
        timestamp_str, logger, level, message = match.groups()

        # Determine log type based on message content
        log_type = "info"
        tool_name = None

        if "🔵 MCP CALL RECEIVED:" in message:
            log_type = "request"
            tool_name = message.split("🔵 MCP CALL RECEIVED:")[1].strip()
        elif "✅ MCP CALL SUCCESS:" in message:
            log_type = "success"
            tool_name = message.split("✅ MCP CALL SUCCESS:")[1].strip()
        elif "❌ MCP CALL ERROR:" in message:
            log_type = "error"
            tool_name = message.split("❌ MCP CALL ERROR:")[1].strip()
        elif "📥 Arguments:" in message:
            log_type = "arguments"
        elif "📤 Result preview:" in message:
            log_type = "result"
        elif "🔴 Error:" in message:
            log_type = "error_detail"
        elif "=" * 10 in message:
            log_type = "separator"

        return {
            "timestamp": timestamp_str,
            "logger": logger,
            "level": level,
            "message": message,
            "log_type": log_type,
            "tool_name": tool_name
        }

    return None


def group_logs_into_calls(logs: List[dict]) -> List[dict]:
    """Group individual log lines into MCP call objects"""
    calls = []
    current_call = None

    for log in logs:
        if log.get("log_type") == "separator":
            continue

        if log.get("log_type") == "request":
            # Start new call
            if current_call:
                calls.append(current_call)
            current_call = {
                "id": len(calls),
                "tool_name": log.get("tool_name"),
                "timestamp": log.get("timestamp"),
                "status": "pending",
                "arguments": None,
                "result": None,
                "error": None,
                "logs": [log]
            }
        elif current_call:
            current_call["logs"].append(log)

            if log.get("log_type") == "arguments":
                # Extract arguments JSON
                try:
                    args_str = log.get("message", "").split("📥 Arguments:")[1].strip()
                    current_call["arguments"] = args_str
                except:
                    pass

            elif log.get("log_type") == "success":
                current_call["status"] = "success"
                current_call["end_timestamp"] = log.get("timestamp")

            elif log.get("log_type") == "error":
                current_call["status"] = "error"
                current_call["end_timestamp"] = log.get("timestamp")

            elif log.get("log_type") == "result":
                try:
                    result_str = log.get("message", "").split("📤 Result preview:")[1].strip()
                    current_call["result"] = result_str
                except:
                    pass

            elif log.get("log_type") == "error_detail":
                try:
                    error_str = log.get("message", "").split("🔴 Error:")[1].strip()
                    current_call["error"] = error_str
                except:
                    pass

    # Don't forget the last call
    if current_call:
        calls.append(current_call)

    return calls


@router.get("")
async def get_mcp_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of log entries to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    tool_filter: Optional[str] = Query(None, description="Filter by tool name"),
    status_filter: Optional[str] = Query(None, description="Filter by status (success/error/pending)"),
    search: Optional[str] = Query(None, description="Search in log messages"),
    db: AsyncSession = Depends(get_db)
):
    """Get MCP call logs with pagination and filtering for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {
            "calls": [],
            "total": 0,
            "message": "No active project found. Please activate a project first."
        }

    log_file = get_log_file_for_project(project.path)

    if not log_file.exists():
        return {
            "calls": [],
            "total": 0,
            "project_name": project.name,
            "project_path": project.path,
            "log_file": str(log_file),
            "message": "No log file found. MCP calls will appear here once the MCP server is running."
        }

    try:
        # Read log file
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Parse all log lines
        parsed_logs = []
        for line in lines:
            parsed = parse_log_line(line)
            if parsed:
                parsed_logs.append(parsed)

        # Group into calls
        calls = group_logs_into_calls(parsed_logs)

        # Apply filters
        if tool_filter:
            calls = [c for c in calls if tool_filter.lower() in (c.get("tool_name") or "").lower()]

        if status_filter:
            calls = [c for c in calls if c.get("status") == status_filter]

        if search:
            search_lower = search.lower()
            calls = [c for c in calls if (
                search_lower in (c.get("tool_name") or "").lower() or
                search_lower in (c.get("arguments") or "").lower() or
                search_lower in (c.get("result") or "").lower() or
                search_lower in (c.get("error") or "").lower()
            )]

        # Sort by timestamp (newest first)
        calls.reverse()

        # Apply pagination
        total = len(calls)
        calls = calls[offset:offset + limit]

        return {
            "calls": calls,
            "total": total,
            "limit": limit,
            "offset": offset,
            "project_name": project.name,
            "project_path": project.path,
            "log_file": str(log_file),
            "log_file_exists": log_file.exists()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


@router.get("/raw")
async def get_raw_logs(
    lines: int = Query(500, ge=1, le=5000, description="Number of lines to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get raw log file content (last N lines) for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {
            "content": "",
            "lines": 0,
            "message": "No active project found"
        }

    log_file = get_log_file_for_project(project.path)

    if not log_file.exists():
        return {
            "content": "",
            "lines": 0,
            "project_name": project.name,
            "message": "No log file found"
        }

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()

        # Get last N lines
        last_lines = all_lines[-lines:]

        return {
            "content": "".join(last_lines),
            "lines": len(last_lines),
            "total_lines": len(all_lines),
            "project_name": project.name,
            "log_file": str(log_file)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


@router.get("/stream/{project_id}")
async def stream_logs(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Stream logs in real-time using Server-Sent Events for a specific project"""

    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    log_file = get_log_file_for_project(project.path)

    async def generate():
        last_position = 0

        while True:
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_content = f.read()
                        last_position = f.tell()

                        if new_content:
                            # Parse new lines
                            new_lines = new_content.strip().split('\n')
                            for line in new_lines:
                                parsed = parse_log_line(line)
                                if parsed:
                                    yield f"data: {json.dumps(parsed)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            # Wait before checking for new content
            await asyncio.sleep(1)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/stats")
async def get_log_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about MCP calls for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {
            "total_calls": 0,
            "success_count": 0,
            "error_count": 0,
            "tools_used": {},
            "log_file_exists": False,
            "message": "No active project found"
        }

    log_file = get_log_file_for_project(project.path)

    if not log_file.exists():
        return {
            "total_calls": 0,
            "success_count": 0,
            "error_count": 0,
            "tools_used": {},
            "project_name": project.name,
            "log_file_exists": False
        }

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_logs = [parse_log_line(line) for line in lines]
        parsed_logs = [l for l in parsed_logs if l]

        calls = group_logs_into_calls(parsed_logs)

        # Calculate stats
        tools_used = {}
        success_count = 0
        error_count = 0

        for call in calls:
            tool = call.get("tool_name", "unknown")
            tools_used[tool] = tools_used.get(tool, 0) + 1

            if call.get("status") == "success":
                success_count += 1
            elif call.get("status") == "error":
                error_count += 1

        # Sort tools by usage
        tools_used = dict(sorted(tools_used.items(), key=lambda x: x[1], reverse=True))

        # Get file stats
        import os
        file_stats = os.stat(log_file)

        return {
            "total_calls": len(calls),
            "success_count": success_count,
            "error_count": error_count,
            "pending_count": len(calls) - success_count - error_count,
            "success_rate": round(success_count / len(calls) * 100, 2) if calls else 0,
            "tools_used": tools_used,
            "unique_tools": len(tools_used),
            "project_name": project.name,
            "log_file": str(log_file),
            "log_file_exists": True,
            "log_file_size_kb": round(file_stats.st_size / 1024, 2),
            "log_file_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate stats: {str(e)}")


@router.delete("")
async def clear_logs(db: AsyncSession = Depends(get_db)):
    """Clear the MCP log file for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {"message": "No active project found"}

    log_file = get_log_file_for_project(project.path)

    if not log_file.exists():
        return {"message": "No log file to clear", "project_name": project.name}

    try:
        # Truncate the file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("")

        return {"message": "Logs cleared successfully", "project_name": project.name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")


# ============================================================================
# HOOKS LOGS ENDPOINTS
# ============================================================================

def get_hooks_log_file_for_project(project_path: str) -> Path:
    """Get the hooks log file path for a specific project"""
    return Path(project_path) / ".claudetask" / "logs" / "hooks" / "hooks.log"


def parse_hook_log_line(line: str) -> Optional[dict]:
    """Parse a single hook log line into a structured format"""
    # Pattern: 2025-11-24 20:30:15 | HOOK_NAME | STATUS | message
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([^|]+) \| ([^|]+) \| (.+)$'
    match = re.match(pattern, line.strip())

    if match:
        timestamp_str, hook_name, status, message = match.groups()
        return {
            "timestamp": timestamp_str.strip(),
            "hook_name": hook_name.strip(),
            "status": status.strip().lower(),
            "message": message.strip()
        }

    # Alternative simpler format: timestamp - level - message
    alt_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},?\d*) - (\w+) - (.+)$'
    alt_match = re.match(alt_pattern, line.strip())

    if alt_match:
        timestamp_str, level, message = alt_match.groups()

        # Try to extract hook name from message
        hook_name = "unknown"
        status = level.lower()

        if "HOOK START:" in message:
            hook_name = message.split("HOOK START:")[1].strip().split()[0]
            status = "start"
        elif "HOOK END:" in message:
            hook_name = message.split("HOOK END:")[1].strip().split()[0]
            status = "success"
        elif "HOOK ERROR:" in message:
            hook_name = message.split("HOOK ERROR:")[1].strip().split()[0]
            status = "error"
        elif "HOOK SKIP:" in message:
            hook_name = message.split("HOOK SKIP:")[1].strip().split()[0]
            status = "skipped"

        return {
            "timestamp": timestamp_str.strip(),
            "hook_name": hook_name,
            "status": status,
            "message": message
        }

    return None


def group_hook_logs_into_executions(logs: List[dict]) -> List[dict]:
    """Group individual hook log lines into execution objects"""
    executions = []
    current_exec = None

    for log in logs:
        if log.get("status") == "start":
            # Start new execution
            if current_exec:
                executions.append(current_exec)
            current_exec = {
                "id": len(executions),
                "hook_name": log.get("hook_name"),
                "timestamp": log.get("timestamp"),
                "status": "running",
                "message": log.get("message"),
                "logs": [log],
                "duration_ms": None
            }
        elif current_exec and log.get("hook_name") == current_exec.get("hook_name"):
            current_exec["logs"].append(log)

            if log.get("status") == "success":
                current_exec["status"] = "success"
                current_exec["end_timestamp"] = log.get("timestamp")
            elif log.get("status") == "error":
                current_exec["status"] = "error"
                current_exec["error"] = log.get("message")
                current_exec["end_timestamp"] = log.get("timestamp")
            elif log.get("status") == "skipped":
                current_exec["status"] = "skipped"
                current_exec["end_timestamp"] = log.get("timestamp")
        else:
            # Standalone log entry (not part of a start/end pair)
            executions.append({
                "id": len(executions),
                "hook_name": log.get("hook_name"),
                "timestamp": log.get("timestamp"),
                "status": log.get("status", "info"),
                "message": log.get("message"),
                "logs": [log],
                "duration_ms": None
            })

    # Don't forget the last execution
    if current_exec:
        executions.append(current_exec)

    return executions


@router.get("/hooks")
async def get_hooks_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of log entries to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    hook_filter: Optional[str] = Query(None, description="Filter by hook name"),
    status_filter: Optional[str] = Query(None, description="Filter by status (success/error/running/skipped)"),
    search: Optional[str] = Query(None, description="Search in log messages"),
    db: AsyncSession = Depends(get_db)
):
    """Get Hook execution logs with pagination and filtering for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {
            "executions": [],
            "total": 0,
            "message": "No active project found. Please activate a project first."
        }

    log_file = get_hooks_log_file_for_project(project.path)

    if not log_file.exists():
        return {
            "executions": [],
            "total": 0,
            "project_name": project.name,
            "project_path": project.path,
            "log_file": str(log_file),
            "message": "No hook logs found. Hook executions will appear here once hooks are triggered."
        }

    try:
        # Read log file
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Parse all log lines
        parsed_logs = []
        for line in lines:
            parsed = parse_hook_log_line(line)
            if parsed:
                parsed_logs.append(parsed)

        # Group into executions
        executions = group_hook_logs_into_executions(parsed_logs)

        # Apply filters
        if hook_filter:
            executions = [e for e in executions if hook_filter.lower() in (e.get("hook_name") or "").lower()]

        if status_filter:
            executions = [e for e in executions if e.get("status") == status_filter]

        if search:
            search_lower = search.lower()
            executions = [e for e in executions if (
                search_lower in (e.get("hook_name") or "").lower() or
                search_lower in (e.get("message") or "").lower() or
                search_lower in (e.get("error") or "").lower()
            )]

        # Sort by timestamp (newest first)
        executions.reverse()

        # Apply pagination
        total = len(executions)
        executions = executions[offset:offset + limit]

        return {
            "executions": executions,
            "total": total,
            "limit": limit,
            "offset": offset,
            "project_name": project.name,
            "project_path": project.path,
            "log_file": str(log_file),
            "log_file_exists": log_file.exists()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read hook logs: {str(e)}")


@router.get("/hooks/stats")
async def get_hooks_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about Hook executions for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {
            "total_executions": 0,
            "success_count": 0,
            "error_count": 0,
            "hooks_used": {},
            "log_file_exists": False,
            "message": "No active project found"
        }

    log_file = get_hooks_log_file_for_project(project.path)

    if not log_file.exists():
        return {
            "total_executions": 0,
            "success_count": 0,
            "error_count": 0,
            "hooks_used": {},
            "project_name": project.name,
            "log_file_exists": False
        }

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        parsed_logs = [parse_hook_log_line(line) for line in lines]
        parsed_logs = [l for l in parsed_logs if l]

        executions = group_hook_logs_into_executions(parsed_logs)

        # Calculate stats
        hooks_used = {}
        success_count = 0
        error_count = 0
        skipped_count = 0

        for exec in executions:
            hook = exec.get("hook_name", "unknown")
            hooks_used[hook] = hooks_used.get(hook, 0) + 1

            if exec.get("status") == "success":
                success_count += 1
            elif exec.get("status") == "error":
                error_count += 1
            elif exec.get("status") == "skipped":
                skipped_count += 1

        # Sort hooks by usage
        hooks_used = dict(sorted(hooks_used.items(), key=lambda x: x[1], reverse=True))

        # Get file stats
        import os
        file_stats = os.stat(log_file)

        return {
            "total_executions": len(executions),
            "success_count": success_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "success_rate": round(success_count / len(executions) * 100, 2) if executions else 0,
            "hooks_used": hooks_used,
            "unique_hooks": len(hooks_used),
            "project_name": project.name,
            "log_file": str(log_file),
            "log_file_exists": True,
            "log_file_size_kb": round(file_stats.st_size / 1024, 2),
            "log_file_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate hook stats: {str(e)}")


@router.delete("/hooks")
async def clear_hooks_logs(db: AsyncSession = Depends(get_db)):
    """Clear the hooks log file for the active project"""

    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()

    if not project:
        return {"message": "No active project found"}

    log_file = get_hooks_log_file_for_project(project.path)

    if not log_file.exists():
        return {"message": "No hook log file to clear", "project_name": project.name}

    try:
        # Truncate the file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("")

        return {"message": "Hook logs cleared successfully", "project_name": project.name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear hook logs: {str(e)}")
