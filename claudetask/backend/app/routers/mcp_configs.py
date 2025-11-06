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
    db: AsyncSession = Depends(get_db)
):
    """
    Enable a default MCP config by merging it to project's .mcp.json

    Process:
    1. Validate MCP config exists in default_mcp_configs table
    2. Merge MCP config from framework-assets/mcp-configs/.mcp.json to project
    3. Insert record into project_mcp_configs junction table
    4. Return enabled MCP config details
    """
    try:
        service = MCPConfigService(db)
        return await service.enable_mcp_config(project_id, mcp_config_id)
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
