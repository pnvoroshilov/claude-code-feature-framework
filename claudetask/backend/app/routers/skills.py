"""Skills API router with MongoDB backend"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from ..database_mongodb import get_mongodb
from ..schemas import SkillInDB, SkillCreate, SkillsResponse
from ..services.skill_service_mongodb import SkillServiceMongoDB

router = APIRouter(prefix="/api/projects/{project_id}/skills", tags=["skills"])


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


@router.get("/", response_model=SkillsResponse)
async def get_project_skills(project_id: str):
    """
    Get all skills for a project.

    Returns:
    - enabled: List of currently enabled skills
    - available_default: List of default skills that can be enabled
    - custom: List of user-created custom skills
    - favorites: Favorite skills across all projects
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        return await service.get_project_skills(project_id, project_path)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skills: {str(e)}")


@router.post("/enable/{skill_id}", response_model=SkillInDB)
async def enable_skill(
    project_id: str,
    skill_id: str,
    skill_type: str = "default"
):
    """
    Enable a skill by copying it to project's .claude/skills/.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        return await service.enable_skill(project_id, project_path, skill_id, skill_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable skill: {str(e)}")


@router.post("/disable/{skill_id}")
async def disable_skill(
    project_id: str,
    skill_id: str,
    skill_type: str = "default"
):
    """
    Disable a skill by removing it from project's .claude/skills/.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        await service.disable_skill(project_id, project_path, skill_id, skill_type)
        return {"success": True, "message": "Skill disabled successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable skill: {str(e)}")


@router.post("/enable-all")
async def enable_all_skills(project_id: str):
    """
    Enable all available skills (both default and custom).
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        project_skills = await service.get_project_skills(project_id, project_path)

        enabled_ids = {s.id for s in project_skills.enabled}
        enabled_count = 0
        errors = []

        for skill in project_skills.available_default:
            if skill.id not in enabled_ids:
                try:
                    await service.enable_skill(project_id, project_path, skill.id, "default")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {skill.name}: {str(e)}")

        for skill in project_skills.custom:
            if skill.id not in enabled_ids:
                try:
                    await service.enable_skill(project_id, project_path, skill.id, "custom")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {skill.name}: {str(e)}")

        result = {"success": True, "enabled_count": enabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable all skills: {str(e)}")


@router.post("/disable-all")
async def disable_all_skills(project_id: str):
    """
    Disable all enabled skills.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        project_skills = await service.get_project_skills(project_id, project_path)

        disabled_count = 0
        errors = []

        for skill in project_skills.enabled:
            try:
                await service.disable_skill(project_id, project_path, skill.id, skill.skill_type)
                disabled_count += 1
            except Exception as e:
                errors.append(f"Failed to disable {skill.name}: {str(e)}")

        result = {"success": True, "disabled_count": disabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable all skills: {str(e)}")


@router.post("/create", response_model=SkillInDB)
async def create_custom_skill(
    project_id: str,
    skill_create: SkillCreate,
    background_tasks: BackgroundTasks
):
    """
    Create a custom skill using Claude Code CLI.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        skill = await service.create_custom_skill(project_id, project_path, skill_create)

        background_tasks.add_task(
            service.execute_skill_creation_cli,
            project_id,
            project_path,
            skill.id,
            skill_create.name,
            skill_create.description
        )

        return skill
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create skill: {str(e)}")


@router.delete("/{skill_id}")
async def delete_custom_skill(project_id: str, skill_id: str):
    """
    Delete a custom skill permanently.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        await service.delete_custom_skill(project_id, project_path, skill_id)
        return {"success": True, "message": "Custom skill deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete skill: {str(e)}")


@router.get("/defaults", response_model=List[SkillInDB])
async def get_default_skills(project_id: str):
    """
    Get all default skills catalog.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        return await service.get_default_skills()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default skills: {str(e)}")


@router.get("/agents/{agent_name}/recommended", response_model=List[SkillInDB])
async def get_agent_recommended_skills(project_id: str, agent_name: str):
    """
    Get recommended skills for a specific agent.

    TODO: Implement recommendations in MongoDB
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        # TODO: Implement agent recommendations in MongoDB
        return []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommended skills: {str(e)}")


@router.post("/favorites/save", response_model=SkillInDB)
async def save_to_favorites(
    project_id: str,
    skill_id: str,
    skill_type: str = "custom"
):
    """
    Mark a skill as favorite.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        return await service.save_to_favorites(project_id, project_path, skill_id, skill_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to favorites: {str(e)}")


@router.post("/favorites/remove")
async def remove_from_favorites(
    project_id: str,
    skill_id: str,
    skill_type: str = "custom"
):
    """
    Remove a skill from favorites.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        await service.remove_from_favorites(project_id, skill_id, skill_type)
        return {"success": True, "message": "Removed from favorites successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from favorites: {str(e)}")


@router.patch("/{skill_id}/status")
async def update_skill_status(
    project_id: str,
    skill_id: str,
    status_update: dict
):
    """
    Update custom skill status and archive it.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        await service.update_custom_skill_status(
            project_id=project_id,
            project_path=project_path,
            skill_id=skill_id,
            status=status_update.get("status"),
            error_message=status_update.get("error_message")
        )
        return {"success": True, "message": "Skill status updated and archived successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skill status: {str(e)}")


@router.put("/{skill_id}/content")
async def update_skill_content(
    project_id: str,
    skill_id: str,
    content_update: dict
):
    """
    Update custom skill content through UI.
    """
    try:
        new_content = content_update.get("content")
        if not new_content:
            raise ValueError("Content is required")

        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = SkillServiceMongoDB(mongodb)
        await service.update_custom_skill_content(
            project_id=project_id,
            project_path=project_path,
            skill_id=skill_id,
            new_content=new_content
        )
        return {"success": True, "message": "Skill content updated successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skill content: {str(e)}")
