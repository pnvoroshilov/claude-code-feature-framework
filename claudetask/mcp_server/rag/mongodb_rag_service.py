"""
MongoDB-based RAG Service for Codebase Search

This module provides MongoDB Atlas Vector Search integration for semantic code search,
replacing ChromaDB when storage_mode is 'mongodb'.

Uses Voyage AI voyage-3-large embeddings (1024d) for superior semantic understanding.
"""

import os
import sys
import asyncio
import hashlib
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MongoDBRAGConfig:
    """Configuration for MongoDB RAG service"""
    backend_url: str = "http://localhost:3333"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_default: int = 20


@dataclass
class CodeChunk:
    """Represents a semantic code chunk (compatible with ChromaDB version)"""
    chunk_id: str
    repository: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    summary: str
    language: str
    chunk_type: str
    symbols: List[str]
    score: Optional[float] = None


class MongoDBRAGService:
    """
    MongoDB-based RAG service for semantic code search.

    This service uses the FastAPI backend to perform:
    - Code indexing via Voyage AI embeddings
    - Vector search via MongoDB Atlas Vector Search

    It's designed to be a drop-in replacement for the ChromaDB-based RAGService
    when storage_mode is 'mongodb'.
    """

    def __init__(self, config: MongoDBRAGConfig, project_id: str, project_path: str):
        """
        Initialize MongoDB RAG service.

        Args:
            config: Service configuration
            project_id: Current project ID
            project_path: Path to project root
        """
        self.config = config
        self.project_id = project_id
        self.project_path = project_path
        self._initialized = False

        logger.info(f"MongoDBRAGService initialized for project {project_id}")

    async def initialize(self):
        """Initialize the service - verify backend connection"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.config.backend_url}/api/health")
                if response.status_code == 200:
                    self._initialized = True
                    logger.info("MongoDB RAG service initialized successfully")
                else:
                    logger.warning(f"Backend health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB RAG service: {e}")
            raise

    async def index_exists(self) -> bool:
        """Check if codebase index exists for this project"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.config.backend_url}/api/codebase/{self.project_id}/stats"
                )

                if response.status_code == 200:
                    stats = response.json()
                    return stats.get("total_chunks", 0) > 0

        except Exception as e:
            logger.warning(f"Failed to check index existence: {e}")

        return False

    async def search_codebase(
        self,
        query: str,
        top_k: int = None,
        filters: Optional[Dict] = None
    ) -> List[CodeChunk]:
        """
        Search codebase for relevant code chunks.

        Args:
            query: Natural language query
            top_k: Number of results to return
            filters: Optional metadata filters (language, etc.)

        Returns:
            List of relevant code chunks ranked by relevance
        """
        top_k = top_k or self.config.top_k_default

        try:
            # Build request payload
            payload = {
                "query": query,
                "limit": top_k
            }

            if filters:
                if "language" in filters:
                    payload["language"] = filters["language"]

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config.backend_url}/api/codebase/{self.project_id}/search",
                    json=payload
                )

                if response.status_code == 200:
                    results = response.json()

                    # Convert to CodeChunk objects
                    code_chunks = []
                    for result in results:
                        chunk = CodeChunk(
                            chunk_id=result.get("chunk_id", result.get("id", "")),
                            repository="main",
                            file_path=result.get("file_path", ""),
                            start_line=result.get("start_line", 0),
                            end_line=result.get("end_line", 0),
                            content=result.get("content", ""),
                            summary=result.get("summary", ""),
                            language=result.get("language", "unknown"),
                            chunk_type=result.get("chunk_type", "unknown"),
                            symbols=result.get("symbols", []),
                            score=result.get("score")
                        )
                        code_chunks.append(chunk)

                    logger.info(f"Code search returned {len(code_chunks)} results")
                    return code_chunks

                else:
                    logger.error(f"Search failed: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Codebase search failed: {e}")

        return []

    async def index_codebase(self, repo_path: str):
        """
        Index entire codebase.

        Args:
            repo_path: Path to repository root
        """
        logger.info(f"Starting codebase indexing from {repo_path}")

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout for large repos
                response = await client.post(
                    f"{self.config.backend_url}/api/codebase/{self.project_id}/index",
                    json={
                        "repo_path": repo_path,
                        "full_reindex": True
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Indexing complete: {result.get('indexed_files', 0)} files, "
                        f"{result.get('total_chunks', 0)} chunks"
                    )
                    return result
                else:
                    logger.error(f"Indexing failed: {response.status_code} - {response.text}")
                    raise Exception(f"Indexing failed: {response.text}")

        except Exception as e:
            logger.error(f"Codebase indexing failed: {e}")
            raise

    async def index_files(self, file_paths: List[str], repo_path: str) -> Dict[str, Any]:
        """
        Index specific files.

        Args:
            file_paths: List of file paths to index
            repo_path: Path to repository root

        Returns:
            Statistics about the indexing operation
        """
        logger.info(f"Indexing {len(file_paths)} specific files")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.config.backend_url}/api/codebase/{self.project_id}/index-files",
                    json={
                        "file_paths": file_paths,
                        "repo_path": repo_path
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"File indexing complete: {result.get('indexed_files', 0)} indexed, "
                        f"{result.get('skipped_files', 0)} skipped"
                    )
                    return result
                else:
                    logger.error(f"File indexing failed: {response.status_code} - {response.text}")
                    raise Exception(f"File indexing failed: {response.text}")

        except Exception as e:
            logger.error(f"File indexing failed: {e}")
            raise

    async def update_index_incremental(self, repo_path: str) -> Dict[str, Any]:
        """
        Incrementally update index for changed files.

        Args:
            repo_path: Path to repository root

        Returns:
            Statistics about the reindexing operation
        """
        logger.info(f"Starting incremental reindex for {repo_path}")

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.config.backend_url}/api/codebase/{self.project_id}/reindex",
                    json={"repo_path": repo_path}
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        f"Incremental reindex complete: {result.get('new_files', 0)} new, "
                        f"{result.get('updated_files', 0)} updated"
                    )
                    return result
                else:
                    logger.error(f"Incremental reindex failed: {response.status_code}")
                    raise Exception(f"Reindex failed: {response.text}")

        except Exception as e:
            logger.error(f"Incremental reindexing failed: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics for the project"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.config.backend_url}/api/codebase/{self.project_id}/stats"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.warning(f"Failed to get stats: {e}")

        return {"total_chunks": 0, "total_files": 0}

    # ========================
    # Task History Methods (Placeholders)
    # ========================

    async def find_similar_tasks(
        self,
        task_description: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical tasks.

        TODO: Implement task similarity search via MongoDB

        Args:
            task_description: Description of current task
            top_k: Number of similar tasks to return

        Returns:
            List of similar tasks with their details
        """
        # For now, return empty - will implement later
        logger.info(f"Task similarity search not yet implemented for MongoDB")
        return []

    async def index_task(self, task: Dict[str, Any]):
        """
        Index a completed task.

        TODO: Implement task indexing via MongoDB

        Args:
            task: Task dictionary with all details
        """
        logger.info(f"Task indexing not yet implemented for MongoDB")
        pass


def create_mongodb_rag_service(
    project_id: str,
    project_path: str,
    backend_url: str = "http://localhost:3333"
) -> MongoDBRAGService:
    """
    Factory function to create MongoDB RAG service.

    Args:
        project_id: Project ID
        project_path: Path to project root
        backend_url: Backend API URL

    Returns:
        Configured MongoDBRAGService instance
    """
    config = MongoDBRAGConfig(backend_url=backend_url)
    return MongoDBRAGService(config, project_id, project_path)
