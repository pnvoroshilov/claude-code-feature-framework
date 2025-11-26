"""
Codebase RAG API endpoints for MongoDB Atlas integration.

These endpoints provide:
- Full codebase indexing
- Incremental reindexing
- Semantic code search via MongoDB Atlas Vector Search
- Indexing statistics

All endpoints require MongoDB Atlas storage mode to be configured.
"""

import os
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..database_mongodb import mongodb_manager
from ..repositories.codebase_repository import MongoDBCodebaseRepository
from ..services.codebase_indexer import CodebaseIndexer, CodebaseSearchService
from ..services.embedding_service import VoyageEmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/codebase", tags=["codebase-rag"])


# ==================
# Request/Response Models
# ==================

class IndexRequest(BaseModel):
    """Request to index codebase"""
    repo_path: str
    full_reindex: bool = False


class IndexFilesRequest(BaseModel):
    """Request to index specific files"""
    file_paths: List[str]
    repo_path: str


class SearchRequest(BaseModel):
    """Request to search codebase"""
    query: str
    limit: int = 20
    min_similarity: float = 0.0
    language: Optional[str] = None


class ReindexRequest(BaseModel):
    """Request to reindex codebase"""
    repo_path: str


# ==================
# Helper Functions
# ==================

def get_voyage_api_key() -> str:
    """Get Voyage AI API key from environment"""
    # Try both possible env var names
    api_key = os.getenv("VOYAGE_AI_API_KEY") or os.getenv("VOYAGE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Voyage AI API key not configured. Set VOYAGE_AI_API_KEY in Settings -> Cloud Storage."
        )
    return api_key


async def get_codebase_services(project_id: str):
    """
    Get codebase repository, indexer, and search service.

    Returns:
        Tuple of (repository, indexer, search_service)

    Raises:
        HTTPException: If MongoDB not configured
    """
    if not mongodb_manager.client:
        raise HTTPException(
            status_code=503,
            detail="MongoDB not connected. Configure MongoDB Atlas in Settings → Cloud Storage."
        )

    try:
        db = mongodb_manager.get_database()
        repository = MongoDBCodebaseRepository(db)

        # Ensure indexes exist
        await repository.ensure_indexes()

        # Create embedding service
        api_key = get_voyage_api_key()
        embedding_service = VoyageEmbeddingService(api_key)

        # Create indexer and search service
        indexer = CodebaseIndexer(repository, embedding_service)
        search_service = CodebaseSearchService(repository, embedding_service)

        return repository, indexer, search_service

    except Exception as e:
        logger.error(f"Failed to initialize codebase services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================
# Endpoints
# ==================

@router.post("/{project_id}/index")
async def index_codebase(
    project_id: str,
    request: IndexRequest,
    background_tasks: BackgroundTasks
):
    """
    Index entire codebase for a project.

    This operation can take several minutes for large codebases.
    Consider running in background for large repositories.

    Args:
        project_id: Project ID
        request: Index request with repo_path and full_reindex flag

    Returns:
        Indexing statistics
    """
    repository, indexer, _ = await get_codebase_services(project_id)

    try:
        logger.info(f"Starting codebase indexing for project {project_id}")

        # Run indexing
        stats = await indexer.index_codebase(
            project_id=project_id,
            repo_path=request.repo_path,
            full_reindex=request.full_reindex
        )

        return {
            "status": "success",
            "message": "Codebase indexing completed",
            **stats
        }

    except Exception as e:
        logger.error(f"Indexing failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/index-files")
async def index_files(
    project_id: str,
    request: IndexFilesRequest
):
    """
    Index specific files.

    Use this for:
    - Re-indexing modified files
    - Adding new files to index

    Args:
        project_id: Project ID
        request: List of file paths and repo path

    Returns:
        Indexing statistics
    """
    repository, indexer, _ = await get_codebase_services(project_id)

    try:
        logger.info(f"Indexing {len(request.file_paths)} files for project {project_id}")

        stats = await indexer.index_files(
            project_id=project_id,
            file_paths=request.file_paths,
            repo_path=request.repo_path
        )

        return {
            "status": "success",
            "message": f"Indexed {stats['indexed_files']} files",
            **stats
        }

    except Exception as e:
        logger.error(f"File indexing failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/reindex")
async def reindex_codebase(
    project_id: str,
    request: ReindexRequest
):
    """
    Incrementally reindex changed files.

    Only processes files that have been modified since last indexing.
    Much faster than full reindex for active development.

    Args:
        project_id: Project ID
        request: Reindex request with repo path

    Returns:
        Reindexing statistics
    """
    repository, indexer, _ = await get_codebase_services(project_id)

    try:
        logger.info(f"Starting incremental reindex for project {project_id}")

        stats = await indexer.reindex_changed_files(
            project_id=project_id,
            repo_path=request.repo_path
        )

        return {
            "status": "success",
            "message": "Incremental reindex completed",
            **stats
        }

    except Exception as e:
        logger.error(f"Reindex failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/search")
async def search_codebase(
    project_id: str,
    request: SearchRequest
):
    """
    Search codebase using natural language query.

    Uses MongoDB Atlas Vector Search with Voyage AI embeddings
    for semantic code search.

    Args:
        project_id: Project ID
        request: Search query and options

    Returns:
        List of matching code chunks with similarity scores
    """
    repository, _, search_service = await get_codebase_services(project_id)

    try:
        logger.info(f"Searching codebase for project {project_id}: '{request.query}'")

        results = await search_service.search(
            project_id=project_id,
            query=request.query,
            limit=request.limit,
            min_similarity=request.min_similarity,
            language=request.language
        )

        return results

    except Exception as e:
        logger.error(f"Search failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/stats")
async def get_stats(project_id: str):
    """
    Get indexing statistics for a project.

    Returns:
        - Total chunks indexed
        - Total files indexed
        - Breakdown by language
        - Breakdown by chunk type
    """
    if not mongodb_manager.client:
        return {
            "total_chunks": 0,
            "total_files": 0,
            "status": "mongodb_not_connected"
        }

    try:
        db = mongodb_manager.get_database()
        repository = MongoDBCodebaseRepository(db)

        stats = await repository.get_stats(project_id)
        stats["status"] = "active"

        return stats

    except Exception as e:
        logger.error(f"Failed to get stats for project {project_id}: {e}")
        return {
            "total_chunks": 0,
            "total_files": 0,
            "status": "error",
            "error": str(e)
        }


@router.get("/{project_id}/files")
async def get_indexed_files(project_id: str):
    """
    Get list of all indexed files for a project.

    Returns:
        List of file paths
    """
    if not mongodb_manager.client:
        raise HTTPException(
            status_code=503,
            detail="MongoDB not connected"
        )

    try:
        db = mongodb_manager.get_database()
        repository = MongoDBCodebaseRepository(db)

        files = await repository.get_indexed_files(project_id)

        return {
            "project_id": project_id,
            "total_files": len(files),
            "files": files
        }

    except Exception as e:
        logger.error(f"Failed to get indexed files for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project_index(project_id: str):
    """
    Delete all indexed chunks for a project.

    Use with caution - requires full reindex to restore.

    Args:
        project_id: Project ID

    Returns:
        Number of deleted chunks
    """
    if not mongodb_manager.client:
        raise HTTPException(
            status_code=503,
            detail="MongoDB not connected"
        )

    try:
        db = mongodb_manager.get_database()
        repository = MongoDBCodebaseRepository(db)

        deleted = await repository.delete_by_project(project_id)

        return {
            "status": "success",
            "message": f"Deleted {deleted} chunks for project {project_id}",
            "deleted_chunks": deleted
        }

    except Exception as e:
        logger.error(f"Failed to delete index for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
