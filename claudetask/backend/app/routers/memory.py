"""
Memory Management API Router

Provides endpoints for conversation memory storage and retrieval.
Automatically uses MongoDB or SQLite based on project's storage_mode setting.
"""

import os
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ..database import get_db
from ..repositories.factory import RepositoryFactory
from ..services.embedding_service import VoyageEmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/memory", tags=["memory"])


# ==================
# Request/Response Models
# ==================

class SaveMessageRequest(BaseModel):
    """Request to save a conversation message"""
    message_type: str = Field(..., description="Type of message: user, assistant, system")
    content: str = Field(..., description="Message content")
    task_id: Optional[int] = None
    metadata: Optional[dict] = None


class UpdateSummaryRequest(BaseModel):
    """Request to update project summary"""
    trigger: str = Field(..., description="Trigger type: session_end, important_decision, task_complete")
    new_insights: str = Field(..., description="New insights to add to summary")
    last_summarized_message_id: Optional[str] = None


class SearchRequest(BaseModel):
    """Request to search memory"""
    query: str
    limit: int = 20
    session_id: Optional[str] = None


# ==================
# Helper Functions
# ==================

async def get_embedding_service():
    """Get embedding service based on availability"""
    voyage_key = os.getenv("VOYAGE_AI_API_KEY") or os.getenv("VOYAGE_API_KEY")
    if voyage_key:
        return VoyageEmbeddingService(voyage_key)
    return None


# ==================
# Endpoints
# ==================

@router.post("/messages")
async def save_conversation_message(
    project_id: str,
    request: SaveMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Save a conversation message to project memory.

    Automatically uses MongoDB or SQLite based on project's storage_mode.
    Generates embeddings using Voyage AI (MongoDB) or Sentence Transformers (SQLite).
    """
    try:
        # Get appropriate repository
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        # Prepare metadata
        metadata = request.metadata or {}
        metadata["message_type"] = request.message_type
        if request.task_id:
            metadata["task_id"] = request.task_id

        # Get session_id from metadata if provided
        session_id = metadata.get("session_id")

        # Generate embedding if possible
        embedding = None
        embedding_service = await get_embedding_service()

        if storage_mode == "mongodb" and embedding_service:
            try:
                embeddings = await embedding_service.generate_embeddings([request.content])
                if embeddings:
                    embedding = embeddings[0]
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")

        # Save message
        if hasattr(repo, 'save_message') and embedding:
            message_id = await repo.save_message(
                project_id=project_id,
                content=request.content,
                embedding=embedding,
                metadata=metadata
            )
        else:
            # Fallback: create without embedding
            message_id = await repo.create({
                "project_id": project_id,
                "content": request.content,
                "message_type": request.message_type,
                "session_id": session_id,
                "task_id": request.task_id,
                "timestamp": datetime.utcnow(),
                "metadata": metadata
            })

        logger.info(f"Saved conversation message for project {project_id[:8]}")

        return {
            "success": True,
            "message_id": str(message_id),
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to save conversation message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages")
async def get_conversation_messages(
    project_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation messages for a project.

    Supports filtering by session_id and pagination.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        filters = {"project_id": project_id}
        if session_id:
            filters["session_id"] = session_id

        messages = await repo.list(skip=offset, limit=limit, filters=filters)

        # Format response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.get("id"),
                "content": msg.get("content"),
                "message_type": msg.get("message_type"),
                "session_id": msg.get("session_id"),
                "task_id": msg.get("task_id"),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") and hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp")) if msg.get("timestamp") else None
            })

        return {
            "messages": formatted_messages,
            "total": len(formatted_messages),
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_project_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get project summary.

    Returns accumulated project insights and knowledge.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        summary = await repo.get_summary(project_id)

        if summary:
            return {
                **summary,
                "storage_mode": storage_mode
            }
        else:
            # Return default empty summary
            return {
                "summary": "Project initialized. No summary available yet.",
                "key_decisions": [],
                "tech_stack": [],
                "patterns": [],
                "gotchas": [],
                "last_updated": None,
                "version": 0,
                "storage_mode": storage_mode
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get project summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary/update")
async def update_project_summary(
    project_id: str,
    request: UpdateSummaryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update project summary with new insights.

    Appends new insights to existing summary with timestamp.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        result = await repo.update_summary(
            project_id=project_id,
            summary=request.new_insights,
            trigger=request.trigger,
            last_summarized_message_id=request.last_summarized_message_id
        )

        logger.info(f"Updated project summary for {project_id[:8]}")

        return {
            "success": True,
            **result,
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update project summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_memory_stats(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get memory statistics for a project.

    Returns message count, summary info, and storage mode.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        stats = await repo.get_stats(project_id)

        return {
            **stats,
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/should-summarize")
async def check_should_summarize(
    project_id: str,
    threshold: int = Query(30, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if project needs summarization.

    Returns true if messages since last summary >= threshold.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        result = await repo.should_summarize(project_id, threshold)

        return {
            **result,
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to check should_summarize: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_sessions(
    project_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get unique sessions for a project.

    Returns list of sessions with message counts and timestamps.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        sessions = await repo.get_sessions(project_id, limit)

        return {
            "sessions": sessions,
            "total": len(sessions),
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/current")
async def get_current_session(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent session ID for a project.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        session_id = await repo.get_current_session(project_id)

        return {
            "session_id": session_id,
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get current session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    project_id: str,
    session_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get messages for a specific session.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        messages = await repo.get_session_messages(project_id, session_id, limit)

        # Format response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.get("id"),
                "content": msg.get("content"),
                "message_type": msg.get("message_type"),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") and hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp")) if msg.get("timestamp") else None
            })

        return {
            "session_id": session_id,
            "messages": formatted_messages,
            "total": len(formatted_messages),
            "storage_mode": storage_mode
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get session messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_memory(
    project_id: str,
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search project memory using semantic search.

    Uses MongoDB Atlas Vector Search or ChromaDB based on storage_mode.
    """
    try:
        repo = await RepositoryFactory.get_memory_repository(project_id, db)
        storage_mode = await RepositoryFactory.get_storage_mode_for_project(project_id, db)

        # Generate query embedding
        embedding_service = await get_embedding_service()

        if storage_mode == "mongodb" and embedding_service:
            try:
                embeddings = await embedding_service.generate_embeddings([request.query])
                if embeddings:
                    query_embedding = embeddings[0]

                    # Build filters
                    filters = {}
                    if request.session_id:
                        filters["session_id"] = request.session_id

                    # Perform vector search
                    results = await repo.vector_search(
                        project_id=project_id,
                        query_embedding=query_embedding,
                        limit=request.limit,
                        filters=filters if filters else None
                    )

                    # Format results
                    formatted_results = []
                    for result in results:
                        formatted_results.append({
                            "id": result.get("id"),
                            "content": result.get("content"),
                            "message_type": result.get("message_type"),
                            "session_id": result.get("session_id"),
                            "timestamp": result.get("timestamp").isoformat() if result.get("timestamp") and hasattr(result.get("timestamp"), 'isoformat') else str(result.get("timestamp")) if result.get("timestamp") else None,
                            "score": result.get("score")
                        })

                    return {
                        "query": request.query,
                        "results": formatted_results,
                        "total": len(formatted_results),
                        "storage_mode": storage_mode
                    }

            except Exception as e:
                logger.warning(f"Vector search failed, falling back to text search: {e}")

        # Fallback: simple text search
        messages = await repo.list(limit=request.limit * 2, filters={"project_id": project_id})

        # Filter by query in content
        query_lower = request.query.lower()
        matching = [
            msg for msg in messages
            if query_lower in msg.get("content", "").lower()
        ][:request.limit]

        # Format results
        formatted_results = []
        for msg in matching:
            formatted_results.append({
                "id": msg.get("id"),
                "content": msg.get("content"),
                "message_type": msg.get("message_type"),
                "session_id": msg.get("session_id"),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") and hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp")) if msg.get("timestamp") else None,
                "score": None  # No score for text search
            })

        return {
            "query": request.query,
            "results": formatted_results,
            "total": len(formatted_results),
            "storage_mode": storage_mode,
            "search_type": "text"  # Indicate fallback
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to search memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
