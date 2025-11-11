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
    db: AsyncSession = Depends(get_db)
):
    """
    Enable a default skill by copying it to project's .claude/skills/

    Process:
    1. Validate skill exists in default_skills table
    2. Copy skill file from framework-assets/claude-skills/ to project
    3. Insert record into project_skills junction table
    4. Return enabled skill details
    """
    try:
        service = SkillService(db)
        return await service.enable_skill(project_id, skill_id)
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
        await service.disable_skill(project_id, skill_id)
        return {"success": True, "message": "Skill disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable skill: {str(e)}")


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
