"""Project Instructions API router"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import Project

router = APIRouter(prefix="/api/projects/{project_id}/instructions", tags=["instructions"])


class InstructionsUpdate(BaseModel):
    """Request to update project custom instructions"""
    custom_instructions: str


class InstructionsResponse(BaseModel):
    """Response with project custom instructions"""
    project_id: str
    custom_instructions: str


@router.get("/", response_model=InstructionsResponse)
async def get_project_instructions(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get custom instructions for a project

    Returns:
        - project_id: Project identifier
        - custom_instructions: Custom Claude instructions text
    """
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        return InstructionsResponse(
            project_id=project.id,
            custom_instructions=project.custom_instructions or ""
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project instructions: {str(e)}")


@router.put("/", response_model=InstructionsResponse)
async def update_project_instructions(
    project_id: str,
    request: InstructionsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update custom instructions for a project

    Args:
        project_id: Project identifier
        request: InstructionsUpdate with custom_instructions text

    Returns:
        Updated instructions
    """
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Update custom instructions
        project.custom_instructions = request.custom_instructions

        await db.commit()
        await db.refresh(project)

        # Regenerate CLAUDE.md with updated instructions
        from ..services.project_service import ProjectService
        try:
            await ProjectService.regenerate_claude_md(db, project_id)
        except Exception as e:
            # Log error but don't fail the update
            print(f"Warning: Failed to regenerate CLAUDE.md: {e}")

        return InstructionsResponse(
            project_id=project.id,
            custom_instructions=project.custom_instructions or ""
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update project instructions: {str(e)}")
