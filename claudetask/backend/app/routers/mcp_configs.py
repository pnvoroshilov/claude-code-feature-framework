"""MCP Configs API router with MongoDB backend"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..database_mongodb import get_mongodb
from ..schemas import MCPConfigInDB, MCPConfigCreate, MCPConfigsResponse
from ..services.mcp_config_service_mongodb import MCPConfigServiceMongoDB
from ..services.mcp_search_service import MCPSearchService

router = APIRouter(prefix="/api/projects/{project_id}/mcp-configs", tags=["mcp-configs"])
search_router = APIRouter(prefix="/api/mcp-search", tags=["mcp-search"])


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


@router.get("/", response_model=MCPConfigsResponse)
async def get_project_mcp_configs(project_id: str):
    """
    Get all MCP configs for a project.

    Returns:
    - enabled: List of currently enabled MCP configs
    - available_default: List of default MCP configs that can be enabled
    - custom: List of user-created custom MCP configs
    - favorites: Favorite MCP configs across all projects
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        return await service.get_project_mcp_configs(project_id, project_path)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MCP configs: {str(e)}")


@router.post("/enable/{mcp_config_id}", response_model=MCPConfigInDB)
async def enable_mcp_config(
    project_id: str,
    mcp_config_id: str,
    mcp_config_type: str = "default"
):
    """
    Enable an MCP config by writing it to project's .mcp.json.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        return await service.enable_mcp_config(project_id, project_path, mcp_config_id, mcp_config_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable MCP config: {str(e)}")


@router.post("/disable/{mcp_config_id}")
async def disable_mcp_config(
    project_id: str,
    mcp_config_id: str,
    mcp_config_type: str = "default"
):
    """
    Disable an MCP config by removing it from project's .mcp.json.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        await service.disable_mcp_config(project_id, project_path, mcp_config_id, mcp_config_type)
        return {"success": True, "message": "MCP config disabled successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable MCP config: {str(e)}")


@router.post("/enable-all")
async def enable_all_mcp_configs(project_id: str):
    """
    Enable all available MCP configs (both default and custom).
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        project_configs = await service.get_project_mcp_configs(project_id, project_path)

        enabled_ids = {c.id for c in project_configs.enabled}
        enabled_count = 0
        errors = []

        for config in project_configs.available_default:
            if config.id not in enabled_ids:
                try:
                    await service.enable_mcp_config(project_id, project_path, config.id, "default")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {config.name}: {str(e)}")

        for config in project_configs.custom:
            if config.id not in enabled_ids:
                try:
                    await service.enable_mcp_config(project_id, project_path, config.id, "custom")
                    enabled_count += 1
                except Exception as e:
                    errors.append(f"Failed to enable {config.name}: {str(e)}")

        result = {"success": True, "enabled_count": enabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable all MCP configs: {str(e)}")


@router.post("/disable-all")
async def disable_all_mcp_configs(project_id: str):
    """
    Disable all enabled MCP configs.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        project_configs = await service.get_project_mcp_configs(project_id, project_path)

        disabled_count = 0
        errors = []

        for config in project_configs.enabled:
            try:
                await service.disable_mcp_config(project_id, project_path, config.id, config.mcp_config_type)
                disabled_count += 1
            except Exception as e:
                errors.append(f"Failed to disable {config.name}: {str(e)}")

        result = {"success": True, "disabled_count": disabled_count}
        if errors:
            result["errors"] = errors

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable all MCP configs: {str(e)}")


@router.post("/create", response_model=MCPConfigInDB)
async def create_custom_mcp_config(
    project_id: str,
    config_create: MCPConfigCreate
):
    """
    Create a custom MCP config.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        return await service.create_custom_mcp_config(project_id, project_path, config_create)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create MCP config: {str(e)}")


@router.delete("/{mcp_config_id}")
async def delete_custom_mcp_config(project_id: str, mcp_config_id: str):
    """
    Delete a custom MCP config permanently.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        await service.delete_custom_mcp_config(project_id, project_path, mcp_config_id)
        return {"success": True, "message": "Custom MCP config deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete MCP config: {str(e)}")


@router.get("/defaults", response_model=List[MCPConfigInDB])
async def get_default_mcp_configs(project_id: str):
    """
    Get all default MCP configs catalog.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        return await service.get_default_mcp_configs()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get default MCP configs: {str(e)}")


@router.post("/favorites/{mcp_config_id}", response_model=MCPConfigInDB)
async def save_to_favorites(
    project_id: str,
    mcp_config_id: str,
    mcp_config_type: str = "custom"
):
    """
    Mark an MCP config as favorite.
    """
    try:
        project_path = await get_project_path(project_id)
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        return await service.save_to_favorites(project_id, project_path, mcp_config_id, mcp_config_type)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save MCP to favorites: {str(e)}")


@router.delete("/favorites/{mcp_config_id}")
async def remove_from_favorites(
    project_id: str,
    mcp_config_id: str,
    mcp_config_type: str = "custom"
):
    """
    Remove an MCP config from favorites.
    """
    try:
        await get_project_path(project_id)  # Validate project exists
        mongodb = await get_mongodb()
        service = MCPConfigServiceMongoDB(mongodb)
        await service.remove_from_favorites(project_id, mcp_config_id, mcp_config_type)
        return {"success": True, "message": "MCP config removed from favorites successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove MCP from favorites: {str(e)}")


# MCP Search endpoints (unchanged - no database dependency)
@search_router.get("/search")
async def search_mcp_servers(q: str, max_pages: int = 3):
    """
    Search for MCP servers on mcp.so with pagination support.
    """
    try:
        max_pages = min(max_pages, 5)
        service = MCPSearchService()
        results = await service.search_servers(q, max_pages=max_pages)
        return {"results": results, "count": len(results), "pages_fetched": max_pages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search MCP servers: {str(e)}")


@search_router.get("/server-config")
async def get_server_config(url: str):
    """
    Get detailed configuration for a specific MCP server.
    """
    try:
        service = MCPSearchService()
        config = await service.get_server_config(url)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch server config: {str(e)}")
