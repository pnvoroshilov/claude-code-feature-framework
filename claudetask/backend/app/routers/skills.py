"""Skills API router"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import SkillInDB, SkillCreate, SkillsResponse
from ..services.skill_service import SkillService

router = APIRouter(prefix="/api/projects/{project_id}/skills", tags=["skills"])


@router.get("/", response_model=SkillsResponse)
async def get_project_skills(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all skills for a project

    Returns:
    - enabled: List of currently enabled skills
    - available_default: List of default skills that can be enabled
    - custom: List of user-created custom skills
    """
    try:
        service = SkillService(db)
        return await service.get_project_skills(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skills: {str(e)}")


@router.post("/enable/{skill_id}", response_model=SkillInDB)
async def enable_skill(
    project_id: str,
    skill_id: int,
    skill_type: str = "default",  # Add skill_type parameter with default value
    db: AsyncSession = Depends(get_db)
):
    """
    Enable a skill by copying it to project's .claude/skills/

    Process:
    1. Validate skill exists (default_skills or custom_skills table)
    2. Copy skill file to project's .claude/skills/
    3. Insert record into project_skills junction table
    4. Return enabled skill details
    """
    try:
        service = SkillService(db)
        return await service.enable_skill(project_id, skill_id, skill_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable skill: {str(e)}")


@router.post("/disable/{skill_id}")
async def disable_skill(
    project_id: str,
    skill_id: int,
    skill_type: str = "default",  # Add skill_type parameter with default value
    db: AsyncSession = Depends(get_db)
):
    """
    Disable a skill by removing it from project's .claude/skills/

    Process:
    1. Remove record from project_skills junction table
    2. Delete skill file from .claude/skills/ directory
    3. Keep record in custom_skills if it's a custom skill (don't delete)
    """
    try:
        service = SkillService(db)
        await service.disable_skill(project_id, skill_id, skill_type)
        return {"success": True, "message": "Skill disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable skill: {str(e)}")


@router.post("/enable-all")
async def enable_all_skills(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Enable all available skills (both default and custom)

    Process:
    1. Get all available default skills
    2. Get all custom skills
    3. Enable each skill that isn't already enabled
    4. Return count of newly enabled skills
    """
    try:
        service = SkillService(db)

        # Get current project skills to avoid duplicates
        project_skills = await service.get_project_skills(project_id)
        enabled_ids = {s.id for s in project_skills.enabled}

        # Get all available skills
        available_default = project_skills.available_default
        custom_skills = project_skills.custom

        # Enable all skills that aren't already enabled
        enabled_count = 0
        errors = []

        for skill in available_default:
            if skill.id not in enabled_ids:
                try:
                    await service.enable_skill(project_id, skill.id, "default")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {skill.name}: {str(e)}")

        for skill in custom_skills:
            if skill.id not in enabled_ids:
                try:
                    await service.enable_skill(project_id, skill.id, "custom")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {skill.name}: {str(e)}")

        result = {"success": True, "enabled_count": enabled_count}
        if errors:
            result["errors"] = errors

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable all skills: {str(e)}")


@router.post("/disable-all")
async def disable_all_skills(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Disable all enabled skills

    Process:
    1. Get all enabled skills
    2. Disable each enabled skill
    3. Return count of disabled skills
    """
    try:
        service = SkillService(db)

        # Get currently enabled skills
        project_skills = await service.get_project_skills(project_id)
        enabled_skills = project_skills.enabled

        # Disable all enabled skills
        disabled_count = 0
        errors = []

        for skill in enabled_skills:
            try:
                # skill.skill_type is already "default" or "custom"
                await service.disable_skill(project_id, skill.id, skill.skill_type)
                disabled_count += 1
            except Exception as e:
                errors.append(f"Failed to disable {skill.name}: {str(e)}")

        result = {"success": True, "disabled_count": disabled_count}
        if errors:
            result["errors"] = errors

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable all skills: {str(e)}")


@router.post("/create", response_model=SkillInDB)
async def create_custom_skill(
    project_id: str,
    skill_create: SkillCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom skill using Claude Code CLI

    Process:
    1. Validate skill name uniqueness
    2. Insert record into custom_skills (status: "creating")
    3. Launch background task for Claude Code CLI interaction
    4. Return skill record (status will update when complete)

    Background task:
    - Start Claude terminal session
    - Execute /create-skill command
    - Send skill name and description via terminal
    - Wait for completion (with timeout)
    - Update skill status to "active" or "failed"
    """
    try:
        service = SkillService(db)
        skill = await service.create_custom_skill(project_id, skill_create)

        # Execute Claude CLI interaction in background
        background_tasks.add_task(
            service.execute_skill_creation_cli,
            project_id,
            skill.id,
            skill_create.name,
            skill_create.description
        )

        return skill
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create skill: {str(e)}")


@router.delete("/{skill_id}")
async def delete_custom_skill(
    project_id: str,
    skill_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a custom skill permanently

    Process:
    1. Verify skill is custom (not default)
    2. Remove from project_skills junction table
    3. Delete skill file from .claude/skills/
    4. Delete record from custom_skills table
    """
    try:
        service = SkillService(db)
        await service.delete_custom_skill(project_id, skill_id)
        return {"success": True, "message": "Custom skill deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete skill: {str(e)}")


@router.get("/defaults", response_model=List[SkillInDB])
async def get_default_skills(db: AsyncSession = Depends(get_db)):
    """
    Get all default skills catalog

    Returns list of 10 default skills with metadata
    """
    try:
        service = SkillService(db)
        return await service.get_default_skills()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default skills: {str(e)}")


@router.get("/agents/{agent_name}/recommended", response_model=List[SkillInDB])
async def get_agent_recommended_skills(
    project_id: str,
    agent_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended skills for a specific agent

    Returns skills from agent_skill_recommendations table,
    ordered by priority (1 = highest priority)
    """
    try:
        service = SkillService(db)
        return await service.get_agent_recommended_skills(project_id, agent_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommended skills: {str(e)}")


@router.post("/favorites/save", response_model=SkillInDB)
async def save_to_favorites(
    project_id: str,
    skill_id: int,
    skill_type: str = "custom",
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a skill as favorite

    Process:
    1. Validate skill exists
    2. Set is_favorite = True
    3. Skill appears in Favorites tab

    Note: Favorites are cross-project - they show for all projects
    """
    try:
        service = SkillService(db)
        return await service.save_to_favorites(project_id, skill_id, skill_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to favorites: {str(e)}")


@router.post("/favorites/remove")
async def remove_from_favorites(
    project_id: str,
    skill_id: int,
    skill_type: str = "custom",
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a skill from favorites

    Process:
    1. Validate skill exists
    2. Set is_favorite = False
    3. Skill removed from Favorites tab
    """
    try:
        service = SkillService(db)
        await service.remove_from_favorites(project_id, skill_id, skill_type)
        return {"success": True, "message": "Removed from favorites successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from favorites: {str(e)}")


@router.patch("/{skill_id}/status")
async def update_skill_status(
    project_id: str,
    skill_id: int,
    status_update: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update custom skill status and archive it

    Process:
    1. Update skill status in database
    2. Archive skill to .claudetask/custom-skills/ for persistence
    3. Enable skill if status is "active"

    This endpoint is called by MCP tools after skill creation is complete.
    """
    try:
        service = SkillService(db)
        await service.update_custom_skill_status(
            project_id=project_id,
            skill_id=skill_id,
            status=status_update.get("status"),
            error_message=status_update.get("error_message")
        )
        return {"success": True, "message": "Skill status updated and archived successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skill status: {str(e)}")


@router.put("/{skill_id}/content")
async def update_skill_content(
    project_id: str,
    skill_id: int,
    content_update: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update custom skill content through UI

    Process:
    1. Update skill content in database
    2. Update archive in .claudetask/custom-skills/
    3. If skill is enabled, update .claude/skills/ as well

    This endpoint is called when user edits skill content through the UI.
    """
    try:
        new_content = content_update.get("content")
        if not new_content:
            raise ValueError("Content is required")

        service = SkillService(db)
        await service.update_custom_skill_content(
            project_id=project_id,
            skill_id=skill_id,
            new_content=new_content
        )
        return {"success": True, "message": "Skill content updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update skill content: {str(e)}")
