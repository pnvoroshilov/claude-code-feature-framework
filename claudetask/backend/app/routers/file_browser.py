"""File browser API router for project files"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import os
import mimetypes

from ..database import get_db
from ..models import Project
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/api/projects/{project_id}/files", tags=["file-browser"])


class FileItem(BaseModel):
    """File or directory item"""
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = None
    modified: Optional[str] = None
    extension: Optional[str] = None


class FileContent(BaseModel):
    """File content response"""
    path: str
    content: str
    mime_type: str
    size: int


class FileSaveRequest(BaseModel):
    """Request to save file content"""
    path: str
    content: str


@router.get("/browse")
async def browse_files(
    project_id: str,
    path: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Browse files and directories in project"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Get full path
        project_path = Path(project.path)
        if path:
            full_path = project_path / path
        else:
            full_path = project_path

        # Security check - prevent directory traversal
        try:
            full_path = full_path.resolve()
            project_path = project_path.resolve()
            if not str(full_path).startswith(str(project_path)):
                raise HTTPException(status_code=403, detail="Access denied")
        except Exception:
            raise HTTPException(status_code=403, detail="Invalid path")

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        # Get items in directory
        items = []
        try:
            for item in sorted(full_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                # Skip hidden files and common ignore patterns
                if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv', '.git']:
                    continue

                file_item = {
                    "name": item.name,
                    "path": str(item.relative_to(project_path)),
                    "type": "directory" if item.is_dir() else "file"
                }

                if item.is_file():
                    try:
                        stat = item.stat()
                        file_item["size"] = stat.st_size
                        file_item["modified"] = str(stat.st_mtime)
                        file_item["extension"] = item.suffix[1:] if item.suffix else None
                    except Exception:
                        pass

                items.append(file_item)

        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")

        # Build breadcrumb path
        relative_path = full_path.relative_to(project_path)
        breadcrumbs = []
        current = Path("")

        breadcrumbs.append({"name": project.name, "path": ""})

        for part in relative_path.parts:
            current = current / part
            breadcrumbs.append({"name": part, "path": str(current)})

        return {
            "success": True,
            "project_name": project.name,
            "current_path": str(relative_path) if str(relative_path) != "." else "",
            "items": items,
            "breadcrumbs": breadcrumbs
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to browse files: {str(e)}")


@router.get("/read")
async def read_file(
    project_id: str,
    path: str,
    db: AsyncSession = Depends(get_db)
):
    """Read file content"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Get full path
        project_path = Path(project.path)
        full_path = (project_path / path).resolve()

        # Security check
        if not str(full_path).startswith(str(project_path.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")

        # Check file size (limit to 10MB for safety)
        file_size = full_path.stat().st_size
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")

        # Get mime type
        mime_type, _ = mimetypes.guess_type(str(full_path))
        if not mime_type:
            mime_type = "text/plain"

        # Read file content
        try:
            # Try to read as text first
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # If not text, try other encodings
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception:
                raise HTTPException(status_code=415, detail="Binary file not supported")

        return {
            "success": True,
            "path": path,
            "content": content,
            "mime_type": mime_type,
            "size": file_size,
            "extension": full_path.suffix[1:] if full_path.suffix else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


@router.post("/save")
async def save_file(
    project_id: str,
    request: FileSaveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save file content"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Get full path
        project_path = Path(project.path)
        full_path = (project_path / request.path).resolve()

        # Security check
        if not str(full_path).startswith(str(project_path.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(request.content)

        file_size = full_path.stat().st_size

        return {
            "success": True,
            "path": request.path,
            "size": file_size,
            "message": "File saved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@router.get("/tree")
async def get_file_tree(
    project_id: str,
    path: str = "",
    max_depth: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """Get recursive file tree structure"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        project_path = Path(project.path)
        if path:
            full_path = project_path / path
        else:
            full_path = project_path

        # Security check
        try:
            full_path = full_path.resolve()
            project_path = project_path.resolve()
            if not str(full_path).startswith(str(project_path)):
                raise HTTPException(status_code=403, detail="Access denied")
        except Exception:
            raise HTTPException(status_code=403, detail="Invalid path")

        def build_tree(dir_path: Path, current_depth: int = 0):
            """Recursively build file tree"""
            if current_depth >= max_depth:
                return []

            items = []
            try:
                for item in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    # Skip hidden and ignored
                    if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv', '.git']:
                        continue

                    relative_path = item.relative_to(project_path)
                    node = {
                        "name": item.name,
                        "path": str(relative_path),
                        "type": "directory" if item.is_dir() else "file"
                    }

                    if item.is_dir():
                        node["children"] = build_tree(item, current_depth + 1)
                    else:
                        node["extension"] = item.suffix[1:] if item.suffix else None

                    items.append(node)
            except PermissionError:
                pass

            return items

        tree = build_tree(full_path)

        return {
            "success": True,
            "project_name": project.name,
            "root_path": path,
            "tree": tree
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file tree: {str(e)}")
