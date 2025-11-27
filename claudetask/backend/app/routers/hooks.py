"""Hooks API router with MongoDB backend"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from ..database_mongodb import get_mongodb
from ..schemas import HookInDB, HookCreate, HooksResponse
from ..services.hook_service_mongodb import HookServiceMongoDB

router = APIRouter(prefix="/api/projects/{project_id}/hooks", tags=["hooks"])


async def get_project_path(project_id: str) -> str:
    """
    Get project path from MongoDB.

    Args:
        project_id: Project ID

    Returns:
        Project filesystem path

    Raises:
        HTTPException 404 if project not found
    """
    mongodb = await get_mongodb()
    project = await mongodb.projects.find_one({"_id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project["path"]


@router.get("/", response_model=HooksResponse)
async def get_project_hooks(project_id: str):
    """
    Get all hooks for a project.

    Returns:
    - enabled: List of currently enabled hooks
    - available_default: List of default hooks that can be enabled
    - custom: List of user-created custom hooks
    - favorites: Favorite hooks across all projects
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        return await service.get_project_hooks(project_id, project_path)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hooks: {str(e)}")


@router.post("/enable/{hook_id}", response_model=HookInDB)
async def enable_hook(
    project_id: str,
    hook_id: str,
    hook_type: str = "default"
):
    """
    Enable a hook by merging it into project's .claude/settings.json.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        return await service.enable_hook(project_id, project_path, hook_id, hook_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable hook: {str(e)}")


@router.post("/disable/{hook_id}")
async def disable_hook(
    project_id: str,
    hook_id: str,
    hook_type: str = "default"
):
    """
    Disable a hook by removing it from project's .claude/settings.json.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        await service.disable_hook(project_id, project_path, hook_id, hook_type)
        return {"success": True, "message": "Hook disabled successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable hook: {str(e)}")


@router.post("/enable-all")
async def enable_all_hooks(project_id: str):
    """
    Enable all available hooks (both default and custom).
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        project_hooks = await service.get_project_hooks(project_id, project_path)

        enabled_ids = {h.id for h in project_hooks.enabled}
        enabled_count = 0
        errors = []

        for hook in project_hooks.available_default:
            if hook.id not in enabled_ids:
                try:
                    await service.enable_hook(project_id, project_path, hook.id, "default")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {hook.name}: {str(e)}")

        for hook in project_hooks.custom:
            if hook.id not in enabled_ids:
                try:
                    await service.enable_hook(project_id, project_path, hook.id, "custom")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {hook.name}: {str(e)}")

        result = {"success": True, "enabled_count": enabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable all hooks: {str(e)}")


@router.post("/disable-all")
async def disable_all_hooks(project_id: str):
    """
    Disable all enabled hooks.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        project_hooks = await service.get_project_hooks(project_id, project_path)

        disabled_count = 0
        errors = []

        for hook in project_hooks.enabled:
            try:
                await service.disable_hook(project_id, project_path, hook.id, hook.hook_type)
                disabled_count += 1
            except Exception as e:
                errors.append(f"Failed to disable {hook.name}: {str(e)}")

        result = {"success": True, "disabled_count": disabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable all hooks: {str(e)}")


@router.post("/create", response_model=HookInDB)
async def create_custom_hook(
    project_id: str,
    hook_create: HookCreate,
    background_tasks: BackgroundTasks
):
    """
    Create a custom hook using Claude Code CLI.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        hook = await service.create_custom_hook(project_id, project_path, hook_create)

        background_tasks.add_task(
            service.execute_hook_creation_cli,
            project_id,
            project_path,
            hook.id,
            hook_create.name,
            hook_create.description
        )

        return hook
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create hook: {str(e)}")


@router.delete("/{hook_id}")
async def delete_custom_hook(project_id: str, hook_id: str):
    """
    Delete a custom hook permanently.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        await service.delete_custom_hook(project_id, project_path, hook_id)
        return {"success": True, "message": "Custom hook deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete hook: {str(e)}")


@router.get("/defaults", response_model=List[HookInDB])
async def get_default_hooks(project_id: str):
    """
    Get all default hooks catalog.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        return await service.get_default_hooks()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default hooks: {str(e)}")


@router.post("/favorites/save", response_model=HookInDB)
async def save_to_favorites(
    project_id: str,
    hook_id: str,
    hook_type: str = "custom"
):
    """
    Mark a hook as favorite.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        return await service.save_to_favorites(project_id, project_path, hook_id, hook_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to favorites: {str(e)}")


@router.post("/favorites/remove")
async def remove_from_favorites(
    project_id: str,
    hook_id: str,
    hook_type: str = "custom"
):
    """
    Remove a hook from favorites.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        await service.remove_from_favorites(project_id, hook_id, hook_type)
        return {"success": True, "message": "Removed from favorites successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from favorites: {str(e)}")


@router.patch("/{hook_id}/status")
async def update_hook_status(
    project_id: str,
    hook_id: str,
    status_update: dict
):
    """
    Update custom hook status and archive it.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = HookServiceMongoDB(mongodb)
        await service.update_custom_hook_status(
            project_id=project_id,
            project_path=project_path,
            hook_id=hook_id,
            status=status_update.get("status"),
            error_message=status_update.get("error_message")
        )
        return {"success": True, "message": "Hook status updated successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update hook status: {str(e)}")
