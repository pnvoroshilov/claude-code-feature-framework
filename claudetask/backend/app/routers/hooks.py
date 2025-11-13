"""Hooks API router"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import HookInDB, HookCreate, HooksResponse
from ..services.hook_service import HookService

router = APIRouter(prefix="/api/projects/{project_id}/hooks", tags=["hooks"])


@router.get("/", response_model=HooksResponse)
async def get_project_hooks(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all hooks for a project

    Returns:
    - enabled: List of currently enabled hooks
    - available_default: List of default hooks that can be enabled
    - custom: List of user-created custom hooks
    - favorites: List of favorite hooks (cross-project)
    """
    try:
        service = HookService(db)
        return await service.get_project_hooks(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hooks: {str(e)}")


@router.post("/enable/{hook_id}", response_model=HookInDB)
async def enable_hook(
    project_id: str,
    hook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Enable a hook by merging it into project's .claude/settings.json

    Process:
    1. Validate hook exists in default_hooks or custom_hooks table
    2. Merge hook configuration into .claude/settings.json
    3. Insert record into project_hooks junction table
    4. Return enabled hook details
    """
    try:
        service = HookService(db)
        return await service.enable_hook(project_id, hook_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable hook: {str(e)}")


@router.post("/disable/{hook_id}")
async def disable_hook(
    project_id: str,
    hook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Disable a hook by removing it from project's .claude/settings.json

    Process:
    1. Remove record from project_hooks junction table
    2. Remove hook configuration from .claude/settings.json
    3. Keep record in custom_hooks if it's a custom hook (don't delete)
    """
    try:
        service = HookService(db)
        await service.disable_hook(project_id, hook_id)
        return {"success": True, "message": "Hook disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable hook: {str(e)}")


@router.post("/create", response_model=HookInDB)
async def create_custom_hook(
    project_id: str,
    hook_create: HookCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom hook using Claude Code CLI

    Process:
    1. Validate hook name uniqueness
    2. Insert record into custom_hooks (status: "creating")
    3. Launch background task for Claude Code CLI interaction
    4. Return hook record (status will update when complete)

    Background task:
    - Start Claude terminal session
    - Execute hook creation command
    - Send hook name and description via terminal
    - Wait for completion (with timeout)
    - Update hook status to "active" or "failed"
    """
    try:
        service = HookService(db)
        hook = await service.create_custom_hook(project_id, hook_create)

        # Execute Claude CLI interaction in background
        background_tasks.add_task(
            service.execute_hook_creation_cli,
            project_id,
            hook.id,
            hook_create.name,
            hook_create.description
        )

        return hook
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create hook: {str(e)}")


@router.put("/{hook_id}", response_model=HookInDB)
async def update_hook(
    project_id: str,
    hook_id: int,
    hook_update: HookCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a hook (custom or default)

    Process:
    1. Verify hook exists
    2. Update hook metadata in database
    3. If hook is enabled, update .claude/settings.json with new config
    4. Return updated hook details
    """
    try:
        service = HookService(db)
        return await service.update_hook(project_id, hook_id, hook_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update hook: {str(e)}")


@router.delete("/{hook_id}")
async def delete_custom_hook(
    project_id: str,
    hook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a custom hook permanently

    Process:
    1. Verify hook is custom (not default)
    2. Remove from project_hooks junction table
    3. Remove hook from .claude/settings.json
    4. Delete record from custom_hooks table
    """
    try:
        service = HookService(db)
        await service.delete_custom_hook(project_id, hook_id)
        return {"success": True, "message": "Custom hook deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete hook: {str(e)}")


@router.get("/defaults", response_model=List[HookInDB])
async def get_default_hooks(db: AsyncSession = Depends(get_db)):
    """
    Get all default hooks catalog

    Returns list of default hooks with metadata
    """
    try:
        service = HookService(db)
        return await service.get_default_hooks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default hooks: {str(e)}")


@router.post("/favorites/save", response_model=HookInDB)
async def save_to_favorites(
    project_id: str,
    hook_id: int,
    hook_type: str = "custom",
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a hook as favorite

    Process:
    1. Validate hook exists
    2. Set is_favorite = True
    3. Hook appears in Favorites tab

    Note: Favorites are cross-project - they show for all projects
    """
    try:
        service = HookService(db)
        return await service.save_to_favorites(project_id, hook_id, hook_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to favorites: {str(e)}")


@router.post("/favorites/remove")
async def remove_from_favorites(
    project_id: str,
    hook_id: int,
    hook_type: str = "custom",
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a hook from favorites

    Process:
    1. Validate hook exists
    2. Set is_favorite = False
    3. Hook removed from Favorites tab
    """
    try:
        service = HookService(db)
        await service.remove_from_favorites(project_id, hook_id, hook_type)
        return {"success": True, "message": "Removed from favorites successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from favorites: {str(e)}")
