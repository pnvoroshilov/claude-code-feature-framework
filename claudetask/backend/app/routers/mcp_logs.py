"""MCP & Hooks Logs Router - API endpoints for viewing MCP call logs and Hook execution logs

Logs are stored based on project storage_mode:
- local: File-based logs in {project_path}/.claudetask/logs/
- mongodb: MongoDB collections (mcp_logs, hook_logs)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from typing import Optional
from datetime import datetime
import json
import asyncio

from ..database import get_db
from ..models import Project
from ..repositories.factory import RepositoryFactory
from ..repositories.log_repository import MongoDBLogRepository, FileLogRepository

router = APIRouter(prefix="/api/mcp-logs", tags=["mcp-logs"])


async def get_active_project(db: AsyncSession):
    """Get the active project."""
    result = await db.execute(select(Project).where(Project.is_active == True))
    return result.scalar_one_or_none()


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

    project = await get_active_project(db)

    if not project:
        return {
            "calls": [],
            "total": 0,
            "message": "No active project found. Please activate a project first."
        }

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            # MongoDB storage
            result = await log_repo.get_mcp_logs(
                project_id=str(project.id),
                limit=limit,
                offset=offset,
                tool_filter=tool_filter,
                status_filter=status_filter,
                search=search
            )
            result["project_name"] = project.name
            result["project_path"] = project.path
            result["storage_mode"] = "mongodb"
            return result

        else:
            # File-based storage
            result = await log_repo.get_mcp_logs(
                limit=limit,
                offset=offset,
                tool_filter=tool_filter,
                status_filter=status_filter,
                search=search
            )
            result["project_name"] = project.name
            result["project_path"] = project.path
            result["storage_mode"] = "local"
            return result

    except ValueError as e:
        # MongoDB not connected - fallback to file-based
        log_repo = FileLogRepository(project.path)
        result = await log_repo.get_mcp_logs(
            limit=limit,
            offset=offset,
            tool_filter=tool_filter,
            status_filter=status_filter,
            search=search
        )
        result["project_name"] = project.name
        result["project_path"] = project.path
        result["storage_mode"] = "local"
        result["fallback_reason"] = str(e)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


@router.get("/raw")
async def get_raw_logs(
    lines: int = Query(500, ge=1, le=5000, description="Number of lines to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get raw log file content (last N lines) for the active project - only for file-based storage"""

    project = await get_active_project(db)

    if not project:
        return {
            "content": "",
            "lines": 0,
            "message": "No active project found"
        }

    # Raw logs only available for file-based storage
    log_file = Path(project.path) / ".claudetask" / "logs" / "mcp" / "mcp_calls.log"

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
    """Stream logs in real-time using Server-Sent Events for a specific project - only for file-based storage"""

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    log_file = Path(project.path) / ".claudetask" / "logs" / "mcp" / "mcp_calls.log"

    async def generate():
        import re
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\w+) - (.+)$'

        last_position = 0

        while True:
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_content = f.read()
                        last_position = f.tell()

                        if new_content:
                            new_lines = new_content.strip().split('\n')
                            for line in new_lines:
                                match = re.match(pattern, line.strip())
                                if match:
                                    timestamp_str, logger, level, message = match.groups()
                                    parsed = {
                                        "timestamp": timestamp_str,
                                        "logger": logger,
                                        "level": level,
                                        "message": message
                                    }
                                    yield f"data: {json.dumps(parsed)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

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

    project = await get_active_project(db)

    if not project:
        return {
            "total_calls": 0,
            "success_count": 0,
            "error_count": 0,
            "tools_used": {},
            "log_file_exists": False,
            "message": "No active project found"
        }

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            result = await log_repo.get_mcp_stats(project_id=str(project.id))
            result["project_name"] = project.name
            result["storage_mode"] = "mongodb"
            return result
        else:
            result = await log_repo.get_mcp_stats()
            result["project_name"] = project.name
            result["storage_mode"] = "local"
            return result

    except ValueError as e:
        log_repo = FileLogRepository(project.path)
        result = await log_repo.get_mcp_stats()
        result["project_name"] = project.name
        result["storage_mode"] = "local"
        result["fallback_reason"] = str(e)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate stats: {str(e)}")


@router.delete("")
async def clear_logs(db: AsyncSession = Depends(get_db)):
    """Clear the MCP logs for the active project"""

    project = await get_active_project(db)

    if not project:
        return {"message": "No active project found"}

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            deleted = await log_repo.clear_mcp_logs(project_id=str(project.id))
            return {
                "message": f"Cleared {deleted} log entries",
                "project_name": project.name,
                "storage_mode": "mongodb"
            }
        else:
            result = await log_repo.clear_mcp_logs()
            result["project_name"] = project.name
            result["storage_mode"] = "local"
            return result

    except ValueError as e:
        log_repo = FileLogRepository(project.path)
        result = await log_repo.clear_mcp_logs()
        result["project_name"] = project.name
        result["fallback_reason"] = str(e)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")


# ============================================================================
# HOOKS LOGS ENDPOINTS
# ============================================================================

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

    project = await get_active_project(db)

    if not project:
        return {
            "executions": [],
            "total": 0,
            "message": "No active project found. Please activate a project first."
        }

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            result = await log_repo.get_hook_logs(
                project_id=str(project.id),
                limit=limit,
                offset=offset,
                hook_filter=hook_filter,
                status_filter=status_filter,
                search=search
            )
            result["project_name"] = project.name
            result["project_path"] = project.path
            result["storage_mode"] = "mongodb"
            return result
        else:
            result = await log_repo.get_hook_logs(
                limit=limit,
                offset=offset,
                hook_filter=hook_filter,
                status_filter=status_filter,
                search=search
            )
            result["project_name"] = project.name
            result["project_path"] = project.path
            result["storage_mode"] = "local"
            return result

    except ValueError as e:
        log_repo = FileLogRepository(project.path)
        result = await log_repo.get_hook_logs(
            limit=limit,
            offset=offset,
            hook_filter=hook_filter,
            status_filter=status_filter,
            search=search
        )
        result["project_name"] = project.name
        result["project_path"] = project.path
        result["storage_mode"] = "local"
        result["fallback_reason"] = str(e)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read hook logs: {str(e)}")


@router.get("/hooks/stats")
async def get_hooks_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about Hook executions for the active project"""

    project = await get_active_project(db)

    if not project:
        return {
            "total_executions": 0,
            "success_count": 0,
            "error_count": 0,
            "hooks_used": {},
            "log_file_exists": False,
            "message": "No active project found"
        }

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            result = await log_repo.get_hook_stats(project_id=str(project.id))
            result["project_name"] = project.name
            result["storage_mode"] = "mongodb"
            return result
        else:
            result = await log_repo.get_hook_stats()
            result["project_name"] = project.name
            result["storage_mode"] = "local"
            return result

    except ValueError as e:
        log_repo = FileLogRepository(project.path)
        result = await log_repo.get_hook_stats()
        result["project_name"] = project.name
        result["storage_mode"] = "local"
        result["fallback_reason"] = str(e)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate hook stats: {str(e)}")


@router.delete("/hooks")
async def clear_hooks_logs(db: AsyncSession = Depends(get_db)):
    """Clear the hooks logs for the active project"""

    project = await get_active_project(db)

    if not project:
        return {"message": "No active project found"}

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            deleted = await log_repo.clear_hook_logs(project_id=str(project.id))
            return {
                "message": f"Cleared {deleted} hook log entries",
                "project_name": project.name,
                "storage_mode": "mongodb"
            }
        else:
            result = await log_repo.clear_hook_logs()
            result["project_name"] = project.name
            result["storage_mode"] = "local"
            return result

    except ValueError as e:
        log_repo = FileLogRepository(project.path)
        result = await log_repo.clear_hook_logs()
        result["project_name"] = project.name
        result["fallback_reason"] = str(e)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear hook logs: {str(e)}")


# ============================================================================
# LOG INGESTION ENDPOINTS (for MCP server to write logs)
# ============================================================================

@router.post("/ingest/mcp")
async def ingest_mcp_log(
    tool_name: str,
    status: str,
    arguments: Optional[str] = None,
    result: Optional[str] = None,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Ingest MCP log entry - called by MCP server when storage_mode is mongodb"""

    project = await get_active_project(db)

    if not project:
        raise HTTPException(status_code=400, detail="No active project found")

    # Check if MongoDB mode
    storage_mode = getattr(project, 'storage_mode', 'local')
    if storage_mode != "mongodb":
        return {"message": "Skipped - storage_mode is not mongodb", "storage_mode": storage_mode}

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            log_id = await log_repo.create_mcp_log({
                "project_id": str(project.id),
                "tool_name": tool_name,
                "status": status,
                "arguments": arguments,
                "result": result,
                "error": error
            })
            return {"message": "Log created", "log_id": log_id, "storage_mode": "mongodb"}

        return {"message": "Skipped - not MongoDB storage", "storage_mode": storage_mode}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest log: {str(e)}")


@router.post("/ingest/hook")
async def ingest_hook_log(
    hook_name: str,
    status: str,
    message: Optional[str] = None,
    error: Optional[str] = None,
    duration_ms: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Ingest hook log entry - called by hook executor when storage_mode is mongodb"""

    project = await get_active_project(db)

    if not project:
        raise HTTPException(status_code=400, detail="No active project found")

    # Check if MongoDB mode
    storage_mode = getattr(project, 'storage_mode', 'local')
    if storage_mode != "mongodb":
        return {"message": "Skipped - storage_mode is not mongodb", "storage_mode": storage_mode}

    try:
        log_repo = await RepositoryFactory.get_log_repository(
            project_id=str(project.id),
            project_path=project.path,
            db=db
        )

        if isinstance(log_repo, MongoDBLogRepository):
            log_id = await log_repo.create_hook_log({
                "project_id": str(project.id),
                "hook_name": hook_name,
                "status": status,
                "message": message,
                "error": error,
                "duration_ms": duration_ms
            })
            return {"message": "Log created", "log_id": log_id, "storage_mode": "mongodb"}

        return {"message": "Skipped - not MongoDB storage", "storage_mode": storage_mode}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest log: {str(e)}")
