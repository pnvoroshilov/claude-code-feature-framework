"""Subagents API router"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import SubagentInDB, SubagentCreate, SubagentsResponse
from ..services.subagent_service import SubagentService

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
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom subagent

    Process:
    1. Validate project exists
    2. Validate subagent name uniqueness
    3. Create custom subagent record
    4. Auto-enable the subagent for the project
    5. Return created subagent
    """
    try:
        service = SubagentService(db)
        return await service.create_custom_subagent(project_id, subagent_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
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
