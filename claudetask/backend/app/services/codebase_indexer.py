"""Codebase indexer service for MongoDB Atlas with Voyage AI embeddings"""

import os
import sys
import asyncio
import hashlib
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

# Add chunking module to path
mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp_server"
if str(mcp_server_path) not in sys.path:
    sys.path.insert(0, str(mcp_server_path))

from chunking import GenericChunker, ChunkMetadata
from ..services.embedding_service import VoyageEmbeddingService

logger = logging.getLogger(__name__)


class CodebaseIndexer:
    """
    Service for indexing codebase into MongoDB Atlas with Voyage AI embeddings.

    Features:
    - Full codebase indexing
    - Incremental updates based on file changes
    - Semantic code chunking
    - Voyage AI voyage-3-large embeddings (1024d)
    - MongoDB Atlas Vector Search integration

    Usage:
        indexer = CodebaseIndexer(repository, embedding_service)
        await indexer.index_codebase(project_id, "/path/to/repo")
        await indexer.reindex_changed_files(project_id, "/path/to/repo")
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx',
        '.java', '.cs', '.go', '.rs', '.cpp', '.c',
        '.rb', '.php', '.swift', '.kt', '.scala',
        '.vue', '.svelte', '.html', '.css', '.scss'
    }

    # Directories to skip
    SKIP_DIRS = {
        'node_modules', 'venv', '__pycache__', '.git',
        'dist', 'build', '.next', 'target', 'bin', 'obj',
        '.claudetask', 'worktrees', '.venv', 'env',
        'vendor', 'coverage', '.nyc_output', '.cache'
    }

    def __init__(
        self,
        repository,  # MongoDBCodebaseRepository
        embedding_service: VoyageEmbeddingService,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 100  # Voyage AI batch limit (rate limit: 2000 RPS)
    ):
        """
        Initialize codebase indexer.

        Args:
            repository: MongoDBCodebaseRepository instance
            embedding_service: VoyageEmbeddingService instance
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks
            batch_size: Number of chunks to embed in one batch (max 100)
        """
        self.repository = repository
        self.embedding_service = embedding_service
        self.chunker = GenericChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.batch_size = batch_size

    async def index_codebase(
        self,
        project_id: str,
        repo_path: str,
        full_reindex: bool = False
    ) -> Dict[str, Any]:
        """
        Index entire codebase for a project.

        Args:
            project_id: Project ID
            repo_path: Path to repository root
            full_reindex: If True, delete all existing chunks first

        Returns:
            Statistics about the indexing operation
        """
        logger.info(f"Starting codebase indexing for project {project_id} at {repo_path}")

        if full_reindex:
            deleted = await self.repository.delete_by_project(project_id)
            logger.info(f"Deleted {deleted} existing chunks for full reindex")

        stats = {
            "total_files": 0,
            "indexed_files": 0,
            "skipped_files": 0,
            "total_chunks": 0,
            "errors": []
        }

        # Collect all files to index
        files_to_index = []

        for root, dirs, files in os.walk(repo_path):
            # Skip directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                files_to_index.append((file_path, relative_path))

        stats["total_files"] = len(files_to_index)
        logger.info(f"Found {len(files_to_index)} files to index")

        # Index files in batches
        all_chunks = []

        for file_path, relative_path in files_to_index:
            try:
                chunks = await self._process_file(project_id, file_path, relative_path)
                all_chunks.extend(chunks)
                stats["indexed_files"] += 1

                if stats["indexed_files"] % 10 == 0:
                    logger.info(f"Processed {stats['indexed_files']}/{stats['total_files']} files")

            except Exception as e:
                logger.error(f"Failed to process {relative_path}: {e}")
                stats["errors"].append({"file": relative_path, "error": str(e)})
                stats["skipped_files"] += 1

        # Generate embeddings and save to MongoDB in batches
        if all_chunks:
            stats["total_chunks"] = await self._save_chunks_with_embeddings(project_id, all_chunks)

        logger.info(
            f"Indexing complete: {stats['indexed_files']} files, "
            f"{stats['total_chunks']} chunks, {len(stats['errors'])} errors"
        )

        return stats

    async def index_files(
        self,
        project_id: str,
        file_paths: List[str],
        repo_path: str
    ) -> Dict[str, Any]:
        """
        Index specific files (or re-index existing files).

        Args:
            project_id: Project ID
            file_paths: List of file paths (absolute or relative)
            repo_path: Path to repository root

        Returns:
            Statistics about the indexing operation
        """
        logger.info(f"Indexing {len(file_paths)} specific files")

        stats = {
            "indexed_files": 0,
            "skipped_files": 0,
            "total_chunks": 0,
            "errors": []
        }

        all_chunks = []

        for file_path in file_paths:
            # Convert to absolute path if needed
            if not os.path.isabs(file_path):
                abs_path = os.path.join(repo_path, file_path)
                relative_path = file_path
            else:
                abs_path = file_path
                relative_path = os.path.relpath(abs_path, repo_path)

            # Check file exists and has supported extension
            if not os.path.exists(abs_path):
                stats["errors"].append({"file": relative_path, "error": "File not found"})
                stats["skipped_files"] += 1
                continue

            ext = os.path.splitext(abs_path)[1].lower()
            if ext not in self.SUPPORTED_EXTENSIONS:
                stats["errors"].append({"file": relative_path, "error": f"Unsupported extension: {ext}"})
                stats["skipped_files"] += 1
                continue

            try:
                # Delete existing chunks for this file
                await self.repository.delete_by_file(project_id, relative_path)

                # Process file
                chunks = await self._process_file(project_id, abs_path, relative_path)
                all_chunks.extend(chunks)
                stats["indexed_files"] += 1

            except Exception as e:
                logger.error(f"Failed to index {relative_path}: {e}")
                stats["errors"].append({"file": relative_path, "error": str(e)})
                stats["skipped_files"] += 1

        # Save chunks with embeddings
        if all_chunks:
            stats["total_chunks"] = await self._save_chunks_with_embeddings(project_id, all_chunks)

        return stats

    async def reindex_changed_files(
        self,
        project_id: str,
        repo_path: str
    ) -> Dict[str, Any]:
        """
        Incremental reindex - only process changed files.

        Compares file hashes to detect changes.

        Args:
            project_id: Project ID
            repo_path: Path to repository root

        Returns:
            Statistics about the reindexing operation
        """
        logger.info(f"Starting incremental reindex for project {project_id}")

        # Get existing file hashes from database
        existing_hashes = await self.repository.get_file_hashes(project_id)

        stats = {
            "new_files": 0,
            "updated_files": 0,
            "unchanged_files": 0,
            "deleted_files": 0,
            "total_chunks": 0,
            "errors": []
        }

        files_to_index = []
        current_files: Set[str] = set()

        # Walk through repository
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                current_files.add(relative_path)

                # Calculate current file hash
                try:
                    with open(file_path, 'rb') as f:
                        current_hash = hashlib.sha256(f.read()).hexdigest()
                except Exception as e:
                    logger.warning(f"Failed to read {relative_path}: {e}")
                    continue

                # Check if file changed
                stored_hash = existing_hashes.get(relative_path)

                if stored_hash is None:
                    # New file
                    files_to_index.append((file_path, relative_path, current_hash, "new"))
                    stats["new_files"] += 1
                elif stored_hash != current_hash:
                    # File changed
                    files_to_index.append((file_path, relative_path, current_hash, "updated"))
                    stats["updated_files"] += 1
                else:
                    # File unchanged
                    stats["unchanged_files"] += 1

        # Handle deleted files
        deleted_files = set(existing_hashes.keys()) - current_files
        for deleted_file in deleted_files:
            await self.repository.delete_by_file(project_id, deleted_file)
            stats["deleted_files"] += 1

        # Index new and changed files
        all_chunks = []

        for file_path, relative_path, file_hash, status in files_to_index:
            try:
                if status == "updated":
                    # Delete existing chunks first
                    await self.repository.delete_by_file(project_id, relative_path)

                chunks = await self._process_file(project_id, file_path, relative_path, file_hash)
                all_chunks.extend(chunks)

            except Exception as e:
                logger.error(f"Failed to index {relative_path}: {e}")
                stats["errors"].append({"file": relative_path, "error": str(e)})

        # Save chunks with embeddings
        if all_chunks:
            stats["total_chunks"] = await self._save_chunks_with_embeddings(project_id, all_chunks)

        logger.info(
            f"Incremental reindex complete: {stats['new_files']} new, "
            f"{stats['updated_files']} updated, {stats['deleted_files']} deleted"
        )

        return stats

    async def _process_file(
        self,
        project_id: str,
        file_path: str,
        relative_path: str,
        file_hash: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a single file into chunks.

        Args:
            project_id: Project ID
            file_path: Absolute file path
            relative_path: Relative path from repo root
            file_hash: Pre-calculated file hash (optional)

        Returns:
            List of chunk dictionaries (without embeddings)
        """
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Calculate hash if not provided
        if file_hash is None:
            file_hash = hashlib.sha256(content.encode()).hexdigest()

        # Detect language
        ext = os.path.splitext(file_path)[1].lower()
        language = self._detect_language(ext)

        # Chunk the file
        chunks = self.chunker.chunk_code(content, relative_path, language)

        # Convert to dictionaries
        result = []
        for chunk_content, metadata in chunks:
            summary = self.chunker.generate_summary(chunk_content, metadata)

            result.append({
                "project_id": project_id,
                "file_path": relative_path,
                "content": chunk_content,
                "start_line": metadata.start_line,
                "end_line": metadata.end_line,
                "language": metadata.language,
                "chunk_type": metadata.chunk_type,
                "symbols": metadata.symbols,
                "summary": summary,
                "file_hash": file_hash
            })

        return result

    async def _save_chunks_with_embeddings(
        self,
        project_id: str,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        Generate embeddings and save chunks to MongoDB.

        Processes in batches for efficiency.

        Args:
            project_id: Project ID
            chunks: List of chunk dictionaries

        Returns:
            Number of chunks saved
        """
        saved_count = 0

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]

            # Prepare texts for embedding (summary + content for better semantic understanding)
            texts = [
                f"{chunk['summary']}\n\n{chunk['content']}"
                for chunk in batch
            ]

            try:
                # Generate embeddings
                embeddings = await self.embedding_service.generate_embeddings(
                    texts,
                    input_type="document"
                )

                # Save each chunk with its embedding
                for j, chunk in enumerate(batch):
                    await self.repository.save_chunk(
                        project_id=chunk["project_id"],
                        file_path=chunk["file_path"],
                        content=chunk["content"],
                        embedding=embeddings[j],
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                        language=chunk["language"],
                        chunk_type=chunk["chunk_type"],
                        symbols=chunk["symbols"],
                        summary=chunk["summary"],
                        file_hash=chunk["file_hash"]
                    )
                    saved_count += 1

                logger.debug(f"Saved batch {i // self.batch_size + 1}, total {saved_count} chunks")

            except Exception as e:
                logger.error(f"Failed to save batch: {e}")
                raise

        return saved_count

    def _detect_language(self, ext: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.vue': 'vue',
            '.svelte': 'svelte',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss'
        }
        return language_map.get(ext.lower(), 'unknown')


class CodebaseSearchService:
    """
    Service for semantic code search using MongoDB Atlas Vector Search.

    Provides:
    - Natural language code search
    - Language/type filtering
    - Similarity threshold control
    """

    def __init__(
        self,
        repository,  # MongoDBCodebaseRepository
        embedding_service: VoyageEmbeddingService
    ):
        """
        Initialize search service.

        Args:
            repository: MongoDBCodebaseRepository instance
            embedding_service: VoyageEmbeddingService instance
        """
        self.repository = repository
        self.embedding_service = embedding_service

    async def search(
        self,
        project_id: str,
        query: str,
        limit: int = 20,
        min_similarity: float = 0.0,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search codebase using natural language query.

        Args:
            project_id: Project ID
            query: Natural language search query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0.0-1.0)
            language: Optional language filter (e.g., "python", "typescript")

        Returns:
            List of matching code chunks with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_query_embedding(query)

        # Build filters
        filters = {}
        if language:
            filters["language"] = language

        # Perform vector search
        results = await self.repository.vector_search(
            project_id=project_id,
            query_embedding=query_embedding,
            limit=limit,
            min_similarity=min_similarity,
            filters=filters
        )

        return results

    async def get_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get indexing statistics for a project.

        Args:
            project_id: Project ID

        Returns:
            Statistics dict
        """
        return await self.repository.get_stats(project_id)

    async def get_indexed_files(self, project_id: str) -> List[str]:
        """
        Get list of all indexed files.

        Args:
            project_id: Project ID

        Returns:
            List of file paths
        """
        return await self.repository.get_indexed_files(project_id)
