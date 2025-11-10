"""Subagents API router"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import SubagentInDB, SubagentCreate, SubagentsResponse
from ..services.subagent_service import SubagentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/subagents", tags=["subagents"])


@router.get("/", response_model=SubagentsResponse)
async def get_project_subagents(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all subagents for a project

    Returns:
    - enabled: List of currently enabled subagents
    - available_default: List of default subagents that can be enabled
    - custom: List of user-created custom subagents
    """
    try:
        service = SubagentService(db)
        return await service.get_project_subagents(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subagents: {str(e)}")


@router.post("/enable/{subagent_id}", response_model=SubagentInDB)
async def enable_subagent(
    project_id: str,
    subagent_id: int,
    subagent_kind: str = "default",
    db: AsyncSession = Depends(get_db)
):
    """
    Enable a subagent for a project

    Process:
    1. Validate subagent exists
    2. Insert record into project_subagents junction table
    3. Return enabled subagent details
    """
    try:
        service = SubagentService(db)
        return await service.enable_subagent(project_id, subagent_id, subagent_kind)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable subagent: {str(e)}")


@router.post("/disable/{subagent_id}")
async def disable_subagent(
    project_id: str,
    subagent_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Disable a subagent for a project

    Process:
    1. Remove record from project_subagents junction table
    2. Keep record in custom_subagents if it's a custom subagent (don't delete)
    """
    try:
        service = SubagentService(db)
        await service.disable_subagent(project_id, subagent_id)
        return {"success": True, "message": "Subagent disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable subagent: {str(e)}")


@router.post("/create", response_model=SubagentInDB)
async def create_custom_subagent(
    project_id: str,
    subagent_create: SubagentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom subagent using Claude Code CLI

    Process:
    1. Validate subagent name uniqueness
    2. Insert record into custom_subagents (status: "creating")
    3. Launch background task for Claude Code CLI interaction
    4. Return subagent record (status will update when complete)

    Background task:
    - Start Claude terminal session
    - Execute /create-agent command
    - Send agent name and description via terminal
    - Wait for completion (with timeout)
    - Update subagent status to "active" or "failed"
    """
    try:
        service = SubagentService(db)
        subagent = await service.create_custom_subagent(project_id, subagent_create)

        # Execute Claude CLI interaction in background
        background_tasks.add_task(
            service.execute_subagent_creation_cli,
            project_id,
            subagent.id,
            subagent_create.name,
            subagent_create.description
        )

        return subagent
    except ValueError as e:
        logger.error(f"ValueError creating custom subagent: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception creating custom subagent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create custom subagent: {str(e)}")


@router.delete("/{subagent_id}")
async def delete_custom_subagent(
    project_id: str,
    subagent_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a custom subagent

    Process:
    1. Verify it's a custom subagent for this project
    2. Remove from project_subagents if enabled
    3. Delete from custom_subagents
    """
    try:
        service = SubagentService(db)
        await service.delete_custom_subagent(project_id, subagent_id)
        return {"success": True, "message": "Custom subagent deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete custom subagent: {str(e)}")
