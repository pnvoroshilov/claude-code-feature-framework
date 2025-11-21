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


@router.post("/enable-all")
async def enable_all_subagents(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Enable all available subagents (both default and custom)

    Process:
    1. Get all available default subagents
    2. Get all custom subagents
    3. Enable each subagent that isn't already enabled
    4. Return count of newly enabled subagents
    """
    try:
        service = SubagentService(db)

        # Get current project subagents to avoid duplicates
        project_subagents = await service.get_project_subagents(project_id)
        enabled_ids = {s.id for s in project_subagents.enabled}

        # Get all available subagents
        available_default = project_subagents.available_default
        custom_subagents = project_subagents.custom

        # Enable all subagents that aren't already enabled
        enabled_count = 0
        errors = []

        for subagent in available_default:
            if subagent.id not in enabled_ids:
                try:
                    await service.enable_subagent(project_id, subagent.id, "default")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {subagent.name}: {str(e)}")

        for subagent in custom_subagents:
            if subagent.id not in enabled_ids:
                try:
                    await service.enable_subagent(project_id, subagent.id, "custom")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {subagent.name}: {str(e)}")

        result = {"success": True, "enabled_count": enabled_count}
        if errors:
            result["errors"] = errors

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable all subagents: {str(e)}")


@router.post("/disable-all")
async def disable_all_subagents(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Disable all enabled subagents

    Process:
    1. Get all enabled subagents
    2. Disable each enabled subagent
    3. Return count of disabled subagents
    """
    try:
        service = SubagentService(db)

        # Get currently enabled subagents
        project_subagents = await service.get_project_subagents(project_id)
        enabled_subagents = project_subagents.enabled

        # Disable all enabled subagents
        disabled_count = 0
        errors = []

        for subagent in enabled_subagents:
            try:
                await service.disable_subagent(project_id, subagent.id)
                disabled_count += 1
            except Exception as e:
                errors.append(f"Failed to disable {subagent.name}: {str(e)}")

        result = {"success": True, "disabled_count": disabled_count}
        if errors:
            result["errors"] = errors

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable all subagents: {str(e)}")


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


@router.post("/favorites/{subagent_id}", response_model=SubagentInDB)
async def save_to_favorites(
    project_id: str,
    subagent_id: int,
    subagent_kind: str = "custom",  # "default" or "custom"
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a subagent as favorite

    Process:
    1. Verify subagent exists
    2. Set is_favorite = True
    3. Return updated subagent

    Note: Favorites are global (not project-specific)
    """
    try:
        service = SubagentService(db)
        return await service.save_to_favorites(subagent_id, subagent_kind)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save subagent to favorites: {str(e)}")


@router.delete("/favorites/{subagent_id}")
async def remove_from_favorites(
    subagent_id: int,
    subagent_kind: str = "custom",  # "default" or "custom"
    db: AsyncSession = Depends(get_db)
):
    """
    Unmark a subagent as favorite

    Process:
    1. Verify subagent exists and is marked as favorite
    2. Set is_favorite = False

    Note: project_id is not needed since favorites are just a flag
    """
    try:
        service = SubagentService(db)
        await service.remove_from_favorites(subagent_id, subagent_kind)
        return {"success": True, "message": "Subagent removed from favorites successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove subagent from favorites: {str(e)}")


@router.patch("/{subagent_id}/status")
async def update_subagent_status(
    project_id: str,
    subagent_id: int,
    status_update: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update custom subagent status and archive it

    Process:
    1. Update subagent status in database
    2. Archive subagent to .claudetask/agents/ for persistence
    3. Enable subagent if status is "active"

    This endpoint is called by MCP tools after subagent creation is complete.
    """
    try:
        service = SubagentService(db)
        await service.update_custom_subagent_status(
            project_id=project_id,
            subagent_id=subagent_id,
            status=status_update.get("status"),
            error_message=status_update.get("error_message")
        )
        return {"success": True, "message": "Subagent status updated and archived successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update subagent status: {str(e)}")
