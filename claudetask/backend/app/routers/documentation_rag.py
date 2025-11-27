"""
Documentation RAG API endpoints.

These endpoints provide:
- Full documentation indexing
- Incremental reindexing
- Semantic documentation search via MongoDB Atlas Vector Search
- Indexing statistics
"""

import os
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database_mongodb import mongodb_manager
from ..repositories.documentation_repository import MongoDBDocumentationRepository
from ..services.documentation_indexer import DocumentationIndexer, DocumentationSearchService
from ..services.embedding_service import VoyageEmbeddingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documentation-rag", tags=["documentation-rag"])


# Request/Response Models

class IndexDocumentationRequest(BaseModel):
    """Request to index documentation"""
    repo_path: str
    full_reindex: bool = False


class IndexFilesRequest(BaseModel):
    """Request to index specific documentation files"""
    file_paths: list[str]
    repo_path: str


class ReindexRequest(BaseModel):
    """Request to reindex documentation"""
    repo_path: str


class SearchRequest(BaseModel):
    """Request to search documentation"""
    query: str
    limit: int = 20
    min_similarity: float = 0.0
    doc_type: Optional[str] = None


# Helper functions

async def get_documentation_services(project_id: str):
    """
    Get documentation repository, indexer, and search service.

    Requires MongoDB storage mode with Voyage AI API key.
    """
    # Check MongoDB connection
    if not mongodb_manager.client:
        raise HTTPException(
            status_code=503,
            detail="MongoDB not connected. Configure MongoDB Atlas first."
        )

    # Check Voyage AI API key
    voyage_api_key = os.getenv("VOYAGE_AI_API_KEY") or os.getenv("VOYAGE_API_KEY")
    if not voyage_api_key:
        raise HTTPException(
            status_code=503,
            detail="VOYAGE_AI_API_KEY not configured. Required for documentation embedding."
        )

    try:
        db = mongodb_manager.get_database()
        repository = MongoDBDocumentationRepository(db)

        # Ensure indexes exist
        await repository.ensure_indexes()

        embedding_service = VoyageEmbeddingService(voyage_api_key)
        indexer = DocumentationIndexer(repository, embedding_service)
        search_service = DocumentationSearchService(repository, embedding_service)

        return repository, indexer, search_service

    except Exception as e:
        logger.error(f"Failed to initialize documentation services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints

@router.post("/{project_id}/index")
async def index_documentation(
    project_id: str,
    request: IndexDocumentationRequest
):
    """
    Index documentation files for a project.

    Supports full reindex or incremental indexing.
    Indexes markdown files from docs/, README, CONTRIBUTING, etc.

    Args:
        project_id: Project ID
        request: Index request with repo_path and full_reindex flag

    Returns:
        Indexing statistics
    """
    repository, indexer, _ = await get_documentation_services(project_id)

    try:
        logger.info(f"Starting documentation indexing for project {project_id}")

        stats = await indexer.index_documentation(
            project_id=project_id,
            repo_path=request.repo_path,
            full_reindex=request.full_reindex
        )

        return {
            "status": "success",
            "message": "Documentation indexing completed",
            **stats
        }

    except Exception as e:
        logger.error(f"Documentation indexing failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/index-files")
async def index_documentation_files(
    project_id: str,
    request: IndexFilesRequest
):
    """
    Index specific documentation files.

    Re-indexes existing files or adds new ones.

    Args:
        project_id: Project ID
        request: List of file paths to index

    Returns:
        Indexing statistics
    """
    repository, indexer, _ = await get_documentation_services(project_id)

    try:
        logger.info(f"Indexing {len(request.file_paths)} documentation files for project {project_id}")

        stats = await indexer.index_files(
            project_id=project_id,
            file_paths=request.file_paths,
            repo_path=request.repo_path
        )

        return {
            "status": "success",
            "message": "File indexing completed",
            **stats
        }

    except Exception as e:
        logger.error(f"File indexing failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/reindex")
async def reindex_documentation(
    project_id: str,
    request: ReindexRequest
):
    """
    Incrementally reindex changed documentation files.

    Only processes files that have been modified since last indexing.

    Args:
        project_id: Project ID
        request: Reindex request with repo path

    Returns:
        Reindexing statistics
    """
    repository, indexer, _ = await get_documentation_services(project_id)

    try:
        logger.info(f"Starting incremental documentation reindex for project {project_id}")

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
        logger.error(f"Documentation reindex failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/search")
async def search_documentation(
    project_id: str,
    request: SearchRequest
):
    """
    Search documentation using natural language query.

    Uses MongoDB Atlas Vector Search with voyage-3-large embeddings.

    Args:
        project_id: Project ID
        request: Search parameters

    Returns:
        List of matching documentation chunks with similarity scores
    """
    _, _, search_service = await get_documentation_services(project_id)

    try:
        logger.info(f"Searching documentation for project {project_id}: '{request.query}'")

        results = await search_service.search(
            project_id=project_id,
            query=request.query,
            limit=request.limit,
            min_similarity=request.min_similarity,
            doc_type=request.doc_type
        )

        return {
            "status": "success",
            "query": request.query,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Documentation search failed for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/stats")
async def get_stats(project_id: str):
    """
    Get documentation indexing statistics for a project.

    Returns total chunks, unique files, doc types, and last indexed time.
    """
    repository, _, _ = await get_documentation_services(project_id)

    try:
        stats = await repository.get_stats(project_id)
        stats["status"] = "active"
        return stats

    except Exception as e:
        logger.error(f"Failed to get stats for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/files")
async def get_indexed_files(project_id: str):
    """
    Get list of all indexed documentation files for a project.
    """
    repository, _, _ = await get_documentation_services(project_id)

    try:
        files = await repository.get_indexed_files(project_id)

        return {
            "status": "success",
            "count": len(files),
            "files": files
        }

    except Exception as e:
        logger.error(f"Failed to get indexed files for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project_documentation_index(project_id: str):
    """
    Delete all indexed documentation chunks for a project.

    Use with caution - requires full reindex to restore.
    """
    repository, _, _ = await get_documentation_services(project_id)

    try:
        deleted = await repository.delete_by_project(project_id)

        return {
            "status": "success",
            "message": f"Deleted {deleted} documentation chunks",
            "deleted_count": deleted
        }

    except Exception as e:
        logger.error(f"Failed to delete documentation index for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
