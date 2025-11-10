"""MCP Configs API router"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import MCPConfigInDB, MCPConfigCreate, MCPConfigsResponse
from ..services.mcp_config_service import MCPConfigService

router = APIRouter(prefix="/api/projects/{project_id}/mcp-configs", tags=["mcp-configs"])


@router.get("/", response_model=MCPConfigsResponse)
async def get_project_mcp_configs(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all MCP configs for a project

    Returns:
    - enabled: List of currently enabled MCP configs
    - available_default: List of default MCP configs that can be enabled
    - custom: List of user-created custom MCP configs
    """
    try:
        service = MCPConfigService(db)
        return await service.get_project_mcp_configs(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MCP configs: {str(e)}")


@router.post("/enable/{mcp_config_id}", response_model=MCPConfigInDB)
async def enable_mcp_config(
    project_id: str,
    mcp_config_id: int,
    mcp_config_type: str = "default",
    db: AsyncSession = Depends(get_db)
):
    """
    Enable an MCP config by writing it from DB to project's .mcp.json

    Process:
    1. Check if imported config exists in DB (use imported if available)
    2. Otherwise use default/custom MCP config from DB
    3. Write MCP config from DB to .mcp.json
    4. Insert record into project_mcp_configs junction table
    5. Return enabled MCP config details

    DB is the source of truth - .mcp.json is just the output file
    """
    try:
        service = MCPConfigService(db)
        return await service.enable_mcp_config(project_id, mcp_config_id, mcp_config_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable MCP config: {str(e)}")


@router.post("/disable/{mcp_config_id}")
async def disable_mcp_config(
    project_id: str,
    mcp_config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Disable an MCP config by removing it from project's .mcp.json

    Process:
    1. Remove record from project_mcp_configs junction table
    2. Remove MCP config from .mcp.json file
    3. Keep record in custom_mcp_configs if it's a custom config (don't delete)
    """
    try:
        service = MCPConfigService(db)
        await service.disable_mcp_config(project_id, mcp_config_id)
        return {"success": True, "message": "MCP config disabled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable MCP config: {str(e)}")


@router.post("/create", response_model=MCPConfigInDB)
async def create_custom_mcp_config(
    project_id: str,
    config_create: MCPConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom MCP config

    Process:
    1. Validate config JSON structure
    2. Validate MCP config name uniqueness
    3. Insert record into custom_mcp_configs
    4. Return MCP config record (can be enabled separately)
    """
    try:
        service = MCPConfigService(db)
        return await service.create_custom_mcp_config(project_id, config_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create MCP config: {str(e)}")


@router.delete("/{mcp_config_id}")
async def delete_custom_mcp_config(
    project_id: str,
    mcp_config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a custom MCP config permanently

    Process:
    1. Verify MCP config is custom (not default)
    2. Remove from project_mcp_configs junction table
    3. Remove MCP config from .mcp.json
    4. Delete record from custom_mcp_configs table
    """
    try:
        service = MCPConfigService(db)
        await service.delete_custom_mcp_config(project_id, mcp_config_id)
        return {"success": True, "message": "Custom MCP config deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete MCP config: {str(e)}")


@router.get("/defaults", response_model=List[MCPConfigInDB])
async def get_default_mcp_configs(db: AsyncSession = Depends(get_db)):
    """
    Get all default MCP configs catalog

    Returns list of default MCP server configurations from framework-assets
    """
    try:
        service = MCPConfigService(db)
        return await service.get_default_mcp_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default MCP configs: {str(e)}")


@router.post("/favorites/{mcp_config_id}", response_model=MCPConfigInDB)
async def save_to_favorites(
    project_id: str,
    mcp_config_id: int,
    mcp_config_type: str = "custom",  # "default" or "custom"
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an MCP config as favorite

    Process:
    1. Get MCP config (default or custom)
    2. Set is_favorite = True
    3. Return the updated config

    This makes the MCP appear in Favorites tab
    """
    try:
        service = MCPConfigService(db)
        return await service.save_to_favorites(project_id, mcp_config_id, mcp_config_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save MCP to favorites: {str(e)}")


@router.delete("/favorites/{mcp_config_id}")
async def remove_from_favorites(
    mcp_config_id: int,
    mcp_config_type: str = "custom",  # "default" or "custom"
    db: AsyncSession = Depends(get_db)
):
    """
    Unmark an MCP config as favorite

    Process:
    1. Get MCP config (default or custom)
    2. Set is_favorite = False

    Note: project_id is not needed since favorites are just a flag
    """
    try:
        service = MCPConfigService(db)
        await service.remove_from_favorites(mcp_config_id, mcp_config_type)
        return {"success": True, "message": "MCP config removed from favorites successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove MCP from favorites: {str(e)}")
