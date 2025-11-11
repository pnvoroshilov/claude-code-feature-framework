"""Editor API router for agents and skills"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..services.editor_service import EditorService
from ..models import Project
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/api/projects/{project_id}/editor", tags=["editor"])


class EditRequest(BaseModel):
    """Request to edit agent or skill with Claude"""
    name: str
    instructions: str


class SaveRequest(BaseModel):
    """Request to save agent or skill content"""
    name: str
    content: str


@router.get("/agent/{agent_name}/content")
async def get_agent_content(
    project_id: str,
    agent_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get agent file content for editing"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        editor_service = EditorService()
        content = await editor_service.get_agent_content(project.path, agent_name)

        return {
            "success": True,
            "agent_name": agent_name,
            "content": content
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent content: {str(e)}")


@router.get("/skill/{skill_name}/content")
async def get_skill_content(
    project_id: str,
    skill_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get skill file content for editing"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        editor_service = EditorService()
        content = await editor_service.get_skill_content(project.path, skill_name)

        return {
            "success": True,
            "skill_name": skill_name,
            "content": content
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skill content: {str(e)}")


@router.post("/agent/edit")
async def edit_agent_with_claude(
    project_id: str,
    request: EditRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Edit agent using Claude CLI /edit-agent command

    This will execute: /edit-agent "<name>" "<instructions>"
    """
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        editor_service = EditorService()

        # Validate inputs
        if not editor_service.validate_agent_name(request.name):
            raise HTTPException(status_code=400, detail="Invalid agent name")

        sanitized_instructions = editor_service.sanitize_instructions(request.instructions)
        if not sanitized_instructions:
            raise HTTPException(status_code=400, detail="Edit instructions cannot be empty")

        # Execute edit via Claude
        result = await editor_service.edit_agent_via_claude(
            project_path=project.path,
            agent_name=request.name,
            edit_instructions=sanitized_instructions
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to edit agent"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit agent: {str(e)}")


@router.post("/skill/edit")
async def edit_skill_with_claude(
    project_id: str,
    request: EditRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Edit skill using Claude CLI /edit-skill command

    This will execute: /edit-skill "<name>" "<instructions>"
    """
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        editor_service = EditorService()

        # Validate inputs
        if not editor_service.validate_skill_name(request.name):
            raise HTTPException(status_code=400, detail="Invalid skill name")

        sanitized_instructions = editor_service.sanitize_instructions(request.instructions)
        if not sanitized_instructions:
            raise HTTPException(status_code=400, detail="Edit instructions cannot be empty")

        # Execute edit via Claude
        result = await editor_service.edit_skill_via_claude(
            project_path=project.path,
            skill_name=request.name,
            edit_instructions=sanitized_instructions
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to edit skill"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit skill: {str(e)}")


@router.post("/agent/save")
async def save_agent_content(
    project_id: str,
    request: SaveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save manually edited agent content"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        editor_service = EditorService()

        # Validate inputs
        if not editor_service.validate_agent_name(request.name):
            raise HTTPException(status_code=400, detail="Invalid agent name")

        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Save content
        result = await editor_service.save_agent_content(
            project_path=project.path,
            agent_name=request.name,
            content=request.content
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to save agent"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save agent: {str(e)}")


@router.post("/skill/save")
async def save_skill_content(
    project_id: str,
    request: SaveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save manually edited skill content"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        editor_service = EditorService()

        # Validate inputs
        if not editor_service.validate_skill_name(request.name):
            raise HTTPException(status_code=400, detail="Invalid skill name")

        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Save content
        result = await editor_service.save_skill_content(
            project_path=project.path,
            skill_name=request.name,
            content=request.content
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to save skill"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save skill: {str(e)}")
