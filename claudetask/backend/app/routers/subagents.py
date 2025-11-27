"""Subagents API router with MongoDB backend"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from ..database_mongodb import get_mongodb
from ..schemas import SubagentInDB, SubagentCreate, SubagentsResponse, SubagentSkillAssignment, SubagentSkillAssign
from ..services.subagent_service_mongodb import SubagentServiceMongoDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/subagents", tags=["subagents"])


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


@router.get("/", response_model=SubagentsResponse)
async def get_project_subagents(project_id: str):
    """
    Get all subagents for a project.

    Returns:
    - enabled: List of currently enabled subagents
    - available_default: List of default subagents that can be enabled
    - custom: List of user-created custom subagents
    - favorites: Favorite subagents across all projects
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        return await service.get_project_subagents(project_id, project_path)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subagents: {str(e)}")


@router.post("/enable/{subagent_id}", response_model=SubagentInDB)
async def enable_subagent(
    project_id: str,
    subagent_id: str,
    subagent_kind: str = "default"
):
    """
    Enable a subagent for a project.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        return await service.enable_subagent(project_id, project_path, subagent_id, subagent_kind)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable subagent: {str(e)}")


@router.post("/disable/{subagent_id}")
async def disable_subagent(
    project_id: str,
    subagent_id: str,
    subagent_kind: str = "default"
):
    """
    Disable a subagent for a project.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        await service.disable_subagent(project_id, project_path, subagent_id, subagent_kind)
        return {"success": True, "message": "Subagent disabled successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable subagent: {str(e)}")


@router.post("/enable-all")
async def enable_all_subagents(project_id: str):
    """
    Enable all available subagents (both default and custom).
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        project_subagents = await service.get_project_subagents(project_id, project_path)

        enabled_ids = {s.id for s in project_subagents.enabled}
        enabled_count = 0
        errors = []

        for subagent in project_subagents.available_default:
            if subagent.id not in enabled_ids:
                try:
                    await service.enable_subagent(project_id, project_path, subagent.id, "default")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {subagent.name}: {str(e)}")

        for subagent in project_subagents.custom:
            if subagent.id not in enabled_ids:
                try:
                    await service.enable_subagent(project_id, project_path, subagent.id, "custom")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {subagent.name}: {str(e)}")

        result = {"success": True, "enabled_count": enabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable all subagents: {str(e)}")


@router.post("/disable-all")
async def disable_all_subagents(project_id: str):
    """
    Disable all enabled subagents.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        project_subagents = await service.get_project_subagents(project_id, project_path)

        disabled_count = 0
        errors = []

        for subagent in project_subagents.enabled:
            try:
                await service.disable_subagent(project_id, project_path, subagent.id, subagent.subagent_kind)
                disabled_count += 1
            except Exception as e:
                errors.append(f"Failed to disable {subagent.name}: {str(e)}")

        result = {"success": True, "disabled_count": disabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable all subagents: {str(e)}")


@router.post("/create", response_model=SubagentInDB)
async def create_custom_subagent(
    project_id: str,
    subagent_create: SubagentCreate,
    background_tasks: BackgroundTasks
):
    """
    Create a custom subagent using Claude Code CLI.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        subagent = await service.create_custom_subagent(project_id, project_path, subagent_create)

        background_tasks.add_task(
            service.execute_subagent_creation_cli,
            project_id,
            project_path,
            subagent.id,
            subagent_create.name,
            subagent_create.description
        )

        return subagent
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError creating custom subagent: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception creating custom subagent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create custom subagent: {str(e)}")


@router.delete("/{subagent_id}")
async def delete_custom_subagent(project_id: str, subagent_id: str):
    """
    Delete a custom subagent permanently.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        await service.delete_custom_subagent(project_id, project_path, subagent_id)
        return {"success": True, "message": "Custom subagent deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete custom subagent: {str(e)}")


@router.get("/defaults", response_model=List[SubagentInDB])
async def get_default_subagents(project_id: str):
    """
    Get all default subagents catalog.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        return await service.get_default_subagents()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default subagents: {str(e)}")


@router.post("/favorites/{subagent_id}", response_model=SubagentInDB)
async def save_to_favorites(
    project_id: str,
    subagent_id: str,
    subagent_kind: str = "custom"
):
    """
    Mark a subagent as favorite.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        return await service.save_to_favorites(project_id, project_path, subagent_id, subagent_kind)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save subagent to favorites: {str(e)}")


@router.delete("/favorites/{subagent_id}")
async def remove_from_favorites(
    project_id: str,
    subagent_id: str,
    subagent_kind: str = "custom"
):
    """
    Remove a subagent from favorites.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        await service.remove_from_favorites(project_id, subagent_id, subagent_kind)
        return {"success": True, "message": "Subagent removed from favorites successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove subagent from favorites: {str(e)}")


@router.patch("/{subagent_id}/status")
async def update_subagent_status(
    project_id: str,
    subagent_id: str,
    status_update: dict
):
    """
    Update custom subagent status and archive it.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        await service.update_custom_subagent_status(
            project_id=project_id,
            project_path=project_path,
            subagent_id=subagent_id,
            status=status_update.get("status"),
            error_message=status_update.get("error_message")
        )
        return {"success": True, "message": "Subagent status updated and archived successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update subagent status: {str(e)}")


# ========== Subagent Skills Endpoints ==========


@router.get("/{subagent_id}/skills", response_model=List[SubagentSkillAssignment])
async def get_subagent_skills(
    project_id: str,
    subagent_id: str,
    subagent_kind: str = "default"
):
    """
    Get all skills assigned to a subagent.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)

        # Get subagent
        if subagent_kind == "default":
            subagent = await service.repo.get_default_subagent(subagent_id)
        else:
            subagent = await service.repo.get_custom_subagent(subagent_id)

        if not subagent:
            raise ValueError(f"Subagent {subagent_id} not found")

        # Get skills
        skills = await service.repo.get_subagent_skills(subagent_id, subagent_kind)

        result = []
        for skill_assignment in skills:
            skill_id = skill_assignment["skill_id"]
            skill_type = skill_assignment["skill_type"]

            if skill_type == "default":
                skill = await service.skill_repo.get_default_skill(skill_id)
            else:
                skill = await service.skill_repo.get_custom_skill(skill_id)

            if skill:
                result.append(SubagentSkillAssignment(
                    skill_id=skill_id,
                    skill_type=skill_type,
                    skill_name=skill["name"],
                    skill_description=skill["description"],
                    skill_category=skill.get("category", "General"),
                    skill_file_name=skill.get("file_name", ""),
                    assigned_at=skill_assignment.get("assigned_at")
                ))

        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subagent skills: {str(e)}")


@router.put("/{subagent_id}/skills", response_model=List[SubagentSkillAssignment])
async def set_subagent_skills(
    project_id: str,
    subagent_id: str,
    skills: SubagentSkillAssign,
    subagent_kind: str = "default"
):
    """
    Set all skills for a subagent (replaces existing assignments).
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SubagentServiceMongoDB(mongodb)
        return await service.set_subagent_skills(
            project_id=project_id,
            project_path=project_path,
            subagent_id=subagent_id,
            subagent_kind=subagent_kind,
            skill_ids=skills.skill_ids,
            skill_types=skills.skill_types
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set subagent skills: {str(e)}")
