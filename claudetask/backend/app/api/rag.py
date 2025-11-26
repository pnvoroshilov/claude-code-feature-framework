"""
API endpoints for RAG (Retrieval-Augmented Generation) indexing

Supports both ChromaDB (local) and MongoDB Atlas (cloud) backends
based on project's storage_mode setting.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
import os
from pathlib import Path
from urllib.parse import unquote

from ..database import get_db
from ..models import Project, ProjectSettings

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_project_storage_mode(project_path: str, db: AsyncSession) -> tuple:
    """
    Get storage mode and project ID for a project path.

    Returns:
        Tuple of (storage_mode, project_id)
    """
    # Find project by path
    result = await db.execute(
        select(Project).where(Project.path == project_path)
    )
    project = result.scalar_one_or_none()

    if not project:
        return "local", None

    # Get project settings
    settings_result = await db.execute(
        select(ProjectSettings).where(ProjectSettings.project_id == project.id)
    )
    settings = settings_result.scalar_one_or_none()

    storage_mode = getattr(settings, 'storage_mode', 'local') if settings else 'local'
    return storage_mode, project.id


@router.post("/index-commit-files")
async def index_commit_files(
    project_dir: str = Query(..., description="Project directory path (URL-encoded)"),
    request: dict = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Index specific files from a commit for RAG semantic search

    This endpoint is called by git hooks to automatically index changed files
    after merging to main/master branches.

    Automatically uses MongoDB Atlas if project has storage_mode='mongodb',
    otherwise falls back to local ChromaDB.

    Args:
        project_dir: Project directory path (URL-encoded)
        request: JSON body with file_paths array

    Returns:
        Indexing status and file count
    """
    try:
        # URL-decode the project directory (handles spaces and special characters)
        project_path_str = unquote(project_dir)
        project_path = Path(project_path_str)

        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project directory not found")

        # Extract file paths from request body
        file_paths = request.get("file_paths", []) if request else []

        if not file_paths:
            return {
                "success": True,
                "message": "No files to index",
                "files_indexed": 0
            }

        logger.info(f"RAG indexing request for project: {project_path_str}")
        logger.info(f"Files to index: {len(file_paths)}")

        # Get project storage mode
        storage_mode, project_id = await get_project_storage_mode(project_path_str, db)
        logger.info(f"Storage mode: {storage_mode}, Project ID: {project_id}")

        # Convert relative paths to absolute paths
        absolute_file_paths = []
        for file_path in file_paths:
            if os.path.isabs(file_path):
                absolute_file_paths.append(file_path)
            else:
                absolute_file_paths.append(str(project_path / file_path))

        # Filter out only supported file types
        supported_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go',
                              '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php',
                              '.swift', '.kt', '.rs', '.vue', '.md', '.txt',
                              '.json', '.yaml', '.yml', '.xml', '.html', '.css',
                              '.scss', '.sass', '.sql', '.sh', '.bash'}

        filtered_paths = []
        for file_path in absolute_file_paths:
            ext = Path(file_path).suffix.lower()
            if ext in supported_extensions:
                if Path(file_path).exists():
                    filtered_paths.append(file_path)
                else:
                    logger.warning(f"File not found: {file_path}")
            else:
                logger.debug(f"Skipping unsupported file type: {file_path}")

        if not filtered_paths:
            return {
                "success": True,
                "message": "No supported files to index",
                "files_indexed": 0,
                "total_files": len(absolute_file_paths)
            }

        # Index based on storage mode
        if storage_mode == "mongodb" and project_id:
            # Use MongoDB Atlas + Voyage AI
            result = await _index_files_mongodb(project_id, filtered_paths, project_path_str)
        else:
            # Use local ChromaDB
            result = await _index_files_chromadb(filtered_paths, project_path_str)

        logger.info(f"Successfully indexed {result.get('files_indexed', 0)} files for RAG search ({storage_mode})")

        return {
            "success": True,
            "message": f"Successfully indexed {result.get('files_indexed', 0)} files",
            "files_indexed": result.get('files_indexed', 0),
            "total_files": len(absolute_file_paths),
            "skipped_files": len(absolute_file_paths) - len(filtered_paths),
            "project_path": project_path_str,
            "storage_mode": storage_mode
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error indexing files for RAG: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to index files: {str(e)}")


async def _index_files_mongodb(project_id: str, file_paths: list, repo_path: str) -> dict:
    """Index files using MongoDB Atlas + Voyage AI"""
    from ..database_mongodb import mongodb_manager
    from ..repositories.codebase_repository import MongoDBCodebaseRepository
    from ..services.codebase_indexer import CodebaseIndexer
    from ..services.embedding_service import VoyageEmbeddingService

    # Check MongoDB connection
    if not mongodb_manager.client:
        logger.warning("MongoDB not connected, falling back to ChromaDB")
        return await _index_files_chromadb(file_paths, repo_path)

    # Check Voyage AI key
    voyage_api_key = os.getenv("VOYAGE_AI_API_KEY") or os.getenv("VOYAGE_API_KEY")
    if not voyage_api_key:
        logger.warning("Voyage AI API key not set, falling back to ChromaDB")
        return await _index_files_chromadb(file_paths, repo_path)

    try:
        db = mongodb_manager.get_database()
        repository = MongoDBCodebaseRepository(db)
        embedding_service = VoyageEmbeddingService(voyage_api_key)
        indexer = CodebaseIndexer(repository, embedding_service)

        # Convert absolute paths to relative
        relative_paths = []
        for path in file_paths:
            if os.path.isabs(path):
                relative_paths.append(os.path.relpath(path, repo_path))
            else:
                relative_paths.append(path)

        stats = await indexer.index_files(
            project_id=project_id,
            file_paths=relative_paths,
            repo_path=repo_path
        )

        return {
            "files_indexed": stats.get("indexed_files", 0),
            "total_chunks": stats.get("total_chunks", 0)
        }

    except Exception as e:
        logger.error(f"MongoDB indexing failed: {e}, falling back to ChromaDB")
        return await _index_files_chromadb(file_paths, repo_path)


async def _index_files_chromadb(file_paths: list, repo_path: str) -> dict:
    """Index files using local ChromaDB (fallback)"""
    from claudetask.mcp_server.rag.rag_service import RAGService, RAGConfig

    rag_config = RAGConfig()
    rag_service = RAGService(rag_config)
    await rag_service.initialize()

    await rag_service.index_files(
        file_paths=file_paths,
        repo_path=repo_path
    )

    return {
        "files_indexed": len(file_paths),
        "total_chunks": 0  # ChromaDB doesn't return chunk count easily
    }
