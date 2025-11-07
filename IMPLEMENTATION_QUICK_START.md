# MCP Configs Implementation - Quick Start Guide

## Overview

This document provides a step-by-step guide to implementing MCP Configs management using the existing Skills architecture as a template.

**Total Implementation Time:** ~40-60 hours (including testing)

---

## Part 1: Database Setup (2-3 hours)

### Step 1: Create Models

File: `claudetask/backend/app/models.py`

Add after `AgentSkillRecommendation` class:

```python
class MCPConfig(Base):
    """MCP Configuration templates"""
    __tablename__ = "mcp_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # "Data", "Testing", "Deployment", etc.
    config_type = Column(String(50), nullable=False)  # "default" or "custom"
    file_name = Column(String(100), nullable=False)
    config_content = Column(Text, nullable=False)  # Full JSON config
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomMCPConfig(Base):
    """User-created MCP configs"""
    __tablename__ = "custom_mcp_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    file_name = Column(String(100), nullable=False)
    config_content = Column(Text, nullable=False)  # JSON
    status = Column(String(20), default="active")  # "creating", "active", "failed"
    error_message = Column(Text, nullable=True)
    created_by = Column(String(100), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", backref="custom_mcp_configs")


class ProjectMCPConfig(Base):
    """Junction table for enabled MCP configs per project"""
    __tablename__ = "project_mcp_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    mcp_config_id = Column(Integer, nullable=False)
    config_type = Column(String(10), nullable=False)  # "default" or "custom"
    merged_at = Column(DateTime, default=datetime.utcnow)
    merged_by = Column(String(100), default="user")

    project = relationship("Project", backref="enabled_mcp_configs")


class AgentMCPConfigRecommendation(Base):
    """Recommended MCP configs for each agent"""
    __tablename__ = "agent_mcp_config_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False)
    mcp_config_id = Column(Integer, nullable=False)
    config_type = Column(String(10), nullable=False)  # "default" or "custom"
    priority = Column(Integer, default=3)  # 1-5
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 2: Create Pydantic Schemas

File: `claudetask/backend/app/schemas.py`

Add at the end:

```python
# MCP Config Schemas
class MCPConfigBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)


class MCPConfigCreate(MCPConfigBase):
    config_content: str  # JSON string


class MCPConfigInDB(MCPConfigBase):
    id: int
    config_type: str  # "default" or "custom"
    category: str
    file_name: str
    config_content: str
    is_enabled: bool = False
    status: Optional[str] = None  # For custom configs
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MCPConfigsResponse(BaseModel):
    """Response format for getting project MCP configs"""
    enabled: List[MCPConfigInDB]
    available_default: List[MCPConfigInDB]
    custom: List[MCPConfigInDB]
```

### Step 3: Create Database Migration

```bash
cd claudetask/backend
alembic revision --autogenerate -m "Add MCP config tables"
alembic upgrade head
```

---

## Part 2: Backend Services (8-10 hours)

### Step 1: Create MCPConfigFileService

File: `claudetask/backend/app/services/mcp_config_file_service.py`

```python
"""Service for MCP config file operations"""

import json
import os
import shutil
import logging
import aiofiles
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPConfigFileService:
    """Manages MCP config file operations"""

    def __init__(self):
        self.framework_configs_dir = self._get_framework_configs_dir()

    async def merge_config_to_project(
        self,
        project_path: str,
        config_content: str,
        config_name: str
    ) -> bool:
        """
        Merge MCP config into project's .mcp.json
        
        Process:
        1. Load existing .mcp.json (or create default)
        2. Parse new config JSON
        3. Merge mcpServers section
        4. Validate merged result
        5. Write to .mcp.json (with backup)
        """
        try:
            # Parse new config
            new_config = json.loads(config_content)
            if "mcpServers" not in new_config:
                logger.error("Config missing 'mcpServers' section")
                return False

            # Load existing .mcp.json
            mcp_file = os.path.join(project_path, ".mcp.json")
            if os.path.exists(mcp_file):
                async with aiofiles.open(mcp_file, 'r') as f:
                    existing_content = await f.read()
                existing_config = json.loads(existing_content)
            else:
                existing_config = {"mcpServers": {}}

            # Merge configurations
            existing_config["mcpServers"].update(new_config["mcpServers"])

            # Validate merged config
            if not self._validate_mcp_config(existing_config):
                logger.error("Merged config validation failed")
                return False

            # Write with backup
            backup_file = mcp_file + ".backup"
            if os.path.exists(mcp_file):
                shutil.copy2(mcp_file, backup_file)

            async with aiofiles.open(mcp_file, 'w') as f:
                await f.write(json.dumps(existing_config, indent=2))

            logger.info(f"Merged MCP config {config_name} to {mcp_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to merge MCP config: {e}", exc_info=True)
            return False

    async def remove_config_from_project(
        self,
        project_path: str,
        config_servers: Dict[str, Any]
    ) -> bool:
        """Remove config servers from project's .mcp.json"""
        try:
            mcp_file = os.path.join(project_path, ".mcp.json")
            
            if not os.path.exists(mcp_file):
                logger.warning("No .mcp.json found")
                return True

            async with aiofiles.open(mcp_file, 'r') as f:
                content = await f.read()
            
            config = json.loads(content)
            
            # Remove servers
            for server_name in config_servers.keys():
                if server_name in config.get("mcpServers", {}):
                    del config["mcpServers"][server_name]

            # Write updated config
            async with aiofiles.open(mcp_file, 'w') as f:
                await f.write(json.dumps(config, indent=2))

            logger.info(f"Removed MCP config servers from {mcp_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove MCP config: {e}", exc_info=True)
            return False

    async def regenerate_merged_config(
        self,
        project_path: str,
        enabled_configs: list  # List of (config_name, config_content) tuples
    ) -> bool:
        """
        Regenerate merged .mcp.json from all enabled configs
        
        Creates fresh .mcp.json by merging all enabled configs
        """
        try:
            merged = {"mcpServers": {}}

            # Load existing .mcp.json to preserve user customizations
            mcp_file = os.path.join(project_path, ".mcp.json")
            if os.path.exists(mcp_file):
                async with aiofiles.open(mcp_file, 'r') as f:
                    existing = json.loads(await f.read())
                # Keep servers that are not in our enabled configs
                for server_name, server_config in existing.get("mcpServers", {}).items():
                    # Only keep if it looks like a custom entry (not ours to manage)
                    # Simple heuristic: if not in any enabled config
                    is_managed = any(
                        server_name in json.loads(config_content).get("mcpServers", {})
                        for _, config_content in enabled_configs
                    )
                    if not is_managed:
                        merged["mcpServers"][server_name] = server_config

            # Merge all enabled configs
            for config_name, config_content in enabled_configs:
                config = json.loads(config_content)
                merged["mcpServers"].update(config["mcpServers"])

            # Validate
            if not self._validate_mcp_config(merged):
                logger.error("Regenerated config validation failed")
                return False

            # Write
            backup_file = mcp_file + ".backup"
            if os.path.exists(mcp_file):
                shutil.copy2(mcp_file, backup_file)

            async with aiofiles.open(mcp_file, 'w') as f:
                await f.write(json.dumps(merged, indent=2))

            logger.info(f"Regenerated merged MCP config at {mcp_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to regenerate MCP config: {e}", exc_info=True)
            return False

    def _validate_mcp_config(self, config: Dict[str, Any]) -> bool:
        """Validate MCP config structure"""
        if not isinstance(config, dict):
            return False
        if "mcpServers" not in config:
            return False
        if not isinstance(config["mcpServers"], dict):
            return False
        
        # Each server must have 'command' and 'args'
        for server_name, server_config in config["mcpServers"].items():
            if not isinstance(server_config, dict):
                return False
            if "command" not in server_config:
                return False
            if "args" not in server_config:
                return False
        
        return True

    def _get_framework_configs_dir(self) -> str:
        """Get path to framework-assets/mcp-configs/"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = Path(current_dir).parent.parent.parent.parent
        return os.path.join(project_root, "framework-assets", "mcp-configs")
```

### Step 2: Create MCPConfigService

File: `claudetask/backend/app/services/mcp_config_service.py`

```python
"""Service for managing MCP configurations"""

import json
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..models import (
    Project, MCPConfig, CustomMCPConfig, ProjectMCPConfig,
    AgentMCPConfigRecommendation
)
from ..schemas import MCPConfigInDB, MCPConfigCreate, MCPConfigsResponse
from .mcp_config_file_service import MCPConfigFileService

logger = logging.getLogger(__name__)


class MCPConfigService:
    """Service for managing MCP configurations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = MCPConfigFileService()

    async def get_project_configs(self, project_id: str) -> MCPConfigsResponse:
        """Get all MCP configs for project organized by type"""
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all default configs
        default_configs_result = await self.db.execute(
            select(MCPConfig).where(MCPConfig.is_active == True)
        )
        all_default_configs = default_configs_result.scalars().all()

        # Get enabled configs for this project
        enabled_result = await self.db.execute(
            select(ProjectMCPConfig).where(ProjectMCPConfig.project_id == project_id)
        )
        enabled_project_configs = enabled_result.scalars().all()
        enabled_ids = {
            (pc.mcp_config_id, pc.config_type) for pc in enabled_project_configs
        }

        # Get custom configs for this project
        custom_result = await self.db.execute(
            select(CustomMCPConfig).where(CustomMCPConfig.project_id == project_id)
        )
        custom_configs = custom_result.scalars().all()

        # Organize
        enabled = []
        available_default = []

        for config in all_default_configs:
            is_enabled = (config.id, "default") in enabled_ids
            config_dto = self._to_config_dto(config, "default", is_enabled)
            available_default.append(config_dto)
            if is_enabled:
                enabled.append(config_dto)

        custom_dtos = []
        for config in custom_configs:
            is_enabled = (config.id, "custom") in enabled_ids
            config_dto = self._to_config_dto(config, "custom", is_enabled)
            custom_dtos.append(config_dto)
            if is_enabled:
                enabled.append(config_dto)

        return MCPConfigsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos
        )

    async def enable_config(self, project_id: str, config_id: int) -> MCPConfigInDB:
        """Enable an MCP config"""
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get config
        config_result = await self.db.execute(
            select(MCPConfig).where(MCPConfig.id == config_id)
        )
        config = config_result.scalar_one_or_none()
        if not config:
            raise ValueError(f"Config {config_id} not found")

        # Check if already enabled
        existing = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == config_id,
                    ProjectMCPConfig.config_type == "default"
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Config already enabled")

        # Merge config file
        success = await self.file_service.merge_config_to_project(
            project_path=project.path,
            config_content=config.config_content,
            config_name=config.name
        )
        if not success:
            raise RuntimeError("Failed to merge config file")

        # Insert into project_mcp_configs
        project_config = ProjectMCPConfig(
            project_id=project_id,
            mcp_config_id=config_id,
            config_type="default",
            merged_by="user"
        )
        self.db.add(project_config)
        await self.db.commit()

        logger.info(f"Enabled MCP config {config.name} for project {project_id}")
        return self._to_config_dto(config, "default", True)

    async def disable_config(self, project_id: str, config_id: int):
        """Disable an MCP config"""
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get project_mcp_config
        result = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == config_id
                )
            )
        )
        project_config = result.scalar_one_or_none()
        if not project_config:
            raise ValueError("Config not enabled for project")

        # Get config details
        if project_config.config_type == "default":
            config_result = await self.db.execute(
                select(MCPConfig).where(MCPConfig.id == config_id)
            )
            config = config_result.scalar_one_or_none()
        else:
            config_result = await self.db.execute(
                select(CustomMCPConfig).where(CustomMCPConfig.id == config_id)
            )
            config = config_result.scalar_one_or_none()

        if not config:
            raise ValueError(f"Config {config_id} not found")

        # Parse config to get servers to remove
        try:
            config_json = json.loads(config.config_content)
            servers = config_json.get("mcpServers", {})
        except json.JSONDecodeError:
            raise ValueError("Invalid config JSON")

        # Remove from project .mcp.json
        await self.file_service.remove_config_from_project(
            project_path=project.path,
            config_servers=servers
        )

        # Delete from project_mcp_configs
        await self.db.delete(project_config)
        await self.db.commit()

        logger.info(f"Disabled MCP config {config.name} for project {project_id}")

    async def delete_custom_config(self, project_id: str, config_id: int):
        """Delete a custom MCP config"""
        # Get config
        config_result = await self.db.execute(
            select(CustomMCPConfig).where(
                and_(
                    CustomMCPConfig.id == config_id,
                    CustomMCPConfig.project_id == project_id
                )
            )
        )
        config = config_result.scalar_one_or_none()
        if not config:
            raise ValueError(f"Config {config_id} not found")

        # Disable if enabled
        project_config_result = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == config_id,
                    ProjectMCPConfig.config_type == "custom"
                )
            )
        )
        project_config = project_config_result.scalar_one_or_none()
        if project_config:
            await self.db.delete(project_config)

        # Delete config
        await self.db.delete(config)
        await self.db.commit()

        logger.info(f"Deleted custom MCP config {config.name}")

    # Helper methods

    async def _get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    def _to_config_dto(
        self,
        config: any,
        config_type: str,
        is_enabled: bool
    ) -> MCPConfigInDB:
        """Convert model to DTO"""
        return MCPConfigInDB(
            id=config.id,
            name=config.name,
            description=config.description,
            config_type=config_type,
            category=config.category,
            file_name=config.file_name,
            config_content=config.config_content,
            is_enabled=is_enabled,
            status=getattr(config, "status", None),
            created_by=getattr(config, "created_by", "system"),
            created_at=config.created_at,
            updated_at=config.updated_at
        )
```

---

## Part 3: API Endpoints (4-6 hours)

### Create MCPConfigRouter

File: `claudetask/backend/app/routers/mcp_configs.py`

```python
"""MCP Configurations API router"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import MCPConfigInDB, MCPConfigCreate, MCPConfigsResponse
from ..services.mcp_config_service import MCPConfigService

router = APIRouter(
    prefix="/api/projects/{project_id}/mcp-configs",
    tags=["mcp-configs"]
)


@router.get("/", response_model=MCPConfigsResponse)
async def get_project_configs(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all MCP configs for project"""
    try:
        service = MCPConfigService(db)
        return await service.get_project_configs(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configs: {str(e)}")


@router.post("/enable/{config_id}", response_model=MCPConfigInDB)
async def enable_config(
    project_id: str,
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Enable an MCP config"""
    try:
        service = MCPConfigService(db)
        return await service.enable_config(project_id, config_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable config: {str(e)}")


@router.post("/disable/{config_id}")
async def disable_config(
    project_id: str,
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Disable an MCP config"""
    try:
        service = MCPConfigService(db)
        await service.disable_config(project_id, config_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable config: {str(e)}")


@router.delete("/{config_id}")
async def delete_custom_config(
    project_id: str,
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a custom MCP config"""
    try:
        service = MCPConfigService(db)
        await service.delete_custom_config(project_id, config_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete config: {str(e)}")
```

Add to `claudetask/backend/app/main.py`:
```python
from .routers import mcp_configs
app.include_router(mcp_configs.router)
```

---

## Part 4: Frontend UI (8-10 hours)

Create: `claudetask/frontend/src/pages/MCPConfigs.tsx`

(Mirror the structure of Skills.tsx with JSON validation)

---

## Part 5: Default Configs Seeding (2-3 hours)

Create: `claudetask/backend/app/services/mcp_config_seeding_service.py`

Load default configs from `framework-assets/mcp-configs/*.json` and seed them on startup.

---

## Testing (8-12 hours)

- Unit tests for MCPConfigService
- Integration tests for API endpoints
- E2E tests for UI
- JSON validation tests
- Merge algorithm tests

---

## Checklist

- [ ] Database models created
- [ ] Pydantic schemas created
- [ ] Migrations run
- [ ] MCPConfigFileService implemented
- [ ] MCPConfigService implemented
- [ ] Router endpoints created
- [ ] Router registered in main.py
- [ ] Frontend component created
- [ ] Seeding service created
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Framework configs added to `framework-assets/mcp-configs/`
- [ ] Default configs seeded on startup

---

## Key Files to Review

1. **Skills Reference (Copy this pattern):**
   - `/claudetask/backend/app/models.py` - Skill models
   - `/claudetask/backend/app/services/skill_service.py` - Service layer
   - `/claudetask/backend/app/services/skill_file_service.py` - File operations
   - `/claudetask/backend/app/routers/skills.py` - API endpoints
   - `/claudetask/frontend/src/pages/Skills.tsx` - Frontend

2. **Documentation:**
   - `/SKILLS_AND_MCP_ARCHITECTURE.md` - Full architecture
   - `/SKILLS_ARCHITECTURE_DIAGRAMS.md` - Visual diagrams

---

## Important Notes

1. **JSON Validation:** Always validate MCP config JSON before writing
2. **Backup Strategy:** Keep backup of original .mcp.json before merging
3. **Merge Conflicts:** Design merge algorithm to handle conflicts gracefully
4. **Testing URLs:** Consider impact on Claude CLI startup
5. **Error Recovery:** Restore from backup if merge fails

---

## Next Steps After Implementation

1. Create default MCP configs in `framework-assets/mcp-configs/`:
   - `datadog.json` - Datadog integration
   - `github-actions.json` - GitHub Actions integration
   - `aws-lambda.json` - AWS Lambda integration
   - etc.

2. Seed database with default configs

3. Add UI to Projects page for quick config management

4. Add agent recommendations for MCP configs

5. Document available MCP configs for users
