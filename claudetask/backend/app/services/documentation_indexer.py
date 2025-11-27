"""Documentation indexer service for MongoDB Atlas with Voyage AI embeddings"""

import os
import re
import hashlib
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

from ..services.embedding_service import VoyageEmbeddingService

logger = logging.getLogger(__name__)


class DocumentationIndexer:
    """
    Service for indexing documentation into MongoDB Atlas with Voyage AI embeddings.

    Features:
    - Full documentation indexing (markdown, text files)
    - Incremental updates based on file changes
    - Smart markdown chunking by sections
    - Voyage AI voyage-3-large embeddings (1024d)
    - MongoDB Atlas Vector Search integration

    Usage:
        indexer = DocumentationIndexer(repository, embedding_service)
        await indexer.index_documentation(project_id, "/path/to/repo")
    """

    # Supported documentation file extensions
    SUPPORTED_EXTENSIONS = {
        '.md', '.markdown', '.txt', '.rst', '.adoc'
    }

    # Directories to skip
    SKIP_DIRS = {
        'node_modules', 'venv', '__pycache__', '.git',
        'dist', 'build', '.next', 'target', 'bin', 'obj',
        '.venv', 'env', 'vendor', 'coverage', '.nyc_output', '.cache'
    }

    # Directories to prioritize for documentation
    DOC_DIRS = {'docs', 'doc', 'documentation', 'wiki'}

    def __init__(
        self,
        repository,  # MongoDBDocumentationRepository
        embedding_service: VoyageEmbeddingService,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        batch_size: int = 100  # Voyage AI batch limit (rate limit: 2000 RPS)
    ):
        """
        Initialize documentation indexer.

        Args:
            repository: MongoDBDocumentationRepository instance
            embedding_service: VoyageEmbeddingService instance
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            batch_size: Number of chunks to embed in one batch
        """
        self.repository = repository
        self.embedding_service = embedding_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size

    async def index_documentation(
        self,
        project_id: str,
        repo_path: str,
        full_reindex: bool = False,
        include_root_readme: bool = True
    ) -> Dict[str, Any]:
        """
        Index documentation files for a project.

        Args:
            project_id: Project ID
            repo_path: Path to repository root
            full_reindex: If True, delete all existing chunks first
            include_root_readme: Include README files in root directory

        Returns:
            Statistics about the indexing operation
        """
        logger.info(f"Starting documentation indexing for project {project_id} at {repo_path}")

        if full_reindex:
            deleted = await self.repository.delete_by_project(project_id)
            logger.info(f"Deleted {deleted} existing doc chunks for full reindex")

        stats = {
            "total_files": 0,
            "indexed_files": 0,
            "skipped_files": 0,
            "total_chunks": 0,
            "errors": []
        }

        # Collect documentation files
        files_to_index = []

        # First, collect from docs/ directories
        for root, dirs, files in os.walk(repo_path):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            # Get relative path from repo root
            rel_root = os.path.relpath(root, repo_path)

            # Check if we're in a documentation directory
            is_doc_dir = any(
                d in rel_root.split(os.sep) for d in self.DOC_DIRS
            ) or rel_root == '.'

            for file in files:
                ext = os.path.splitext(file)[1].lower()

                # Include if:
                # 1. In a docs directory with supported extension
                # 2. README/CONTRIBUTING/etc in any directory
                # 3. Root level markdown files
                is_important_file = file.upper().startswith(('README', 'CONTRIBUTING', 'CHANGELOG', 'LICENSE'))

                if ext in self.SUPPORTED_EXTENSIONS:
                    if is_doc_dir or is_important_file or rel_root == '.':
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, repo_path)
                        files_to_index.append((file_path, relative_path))

        stats["total_files"] = len(files_to_index)
        logger.info(f"Found {len(files_to_index)} documentation files to index")

        # Index files
        all_chunks = []

        for file_path, relative_path in files_to_index:
            try:
                chunks = await self._process_file(project_id, file_path, relative_path)
                all_chunks.extend(chunks)
                stats["indexed_files"] += 1

                if stats["indexed_files"] % 5 == 0:
                    logger.info(f"Processed {stats['indexed_files']}/{stats['total_files']} files")

            except Exception as e:
                logger.error(f"Failed to process {relative_path}: {e}")
                stats["errors"].append({"file": relative_path, "error": str(e)})
                stats["skipped_files"] += 1

        # Generate embeddings and save to MongoDB in batches
        if all_chunks:
            stats["total_chunks"] = await self._save_chunks_with_embeddings(project_id, all_chunks)

        logger.info(
            f"Documentation indexing complete: {stats['indexed_files']} files, "
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
        Index specific documentation files.

        Args:
            project_id: Project ID
            file_paths: List of file paths (absolute or relative)
            repo_path: Path to repository root

        Returns:
            Statistics about the indexing operation
        """
        logger.info(f"Indexing {len(file_paths)} specific documentation files")

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

            # Check file exists
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
        Incremental reindex - only process changed documentation files.

        Args:
            project_id: Project ID
            repo_path: Path to repository root

        Returns:
            Statistics about the reindexing operation
        """
        logger.info(f"Starting incremental documentation reindex for project {project_id}")

        # Get existing file hashes
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
            rel_root = os.path.relpath(root, repo_path)
            is_doc_dir = any(d in rel_root.split(os.sep) for d in self.DOC_DIRS) or rel_root == '.'

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                is_important_file = file.upper().startswith(('README', 'CONTRIBUTING', 'CHANGELOG', 'LICENSE'))

                if ext not in self.SUPPORTED_EXTENSIONS:
                    continue

                if not (is_doc_dir or is_important_file or rel_root == '.'):
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
                    files_to_index.append((file_path, relative_path, current_hash, "new"))
                    stats["new_files"] += 1
                elif stored_hash != current_hash:
                    files_to_index.append((file_path, relative_path, current_hash, "updated"))
                    stats["updated_files"] += 1
                else:
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
            f"Incremental doc reindex complete: {stats['new_files']} new, "
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
        """Process a single documentation file into chunks."""
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Calculate hash if not provided
        if file_hash is None:
            file_hash = hashlib.sha256(content.encode()).hexdigest()

        # Detect document type
        ext = os.path.splitext(file_path)[1].lower()
        doc_type = self._detect_doc_type(file_path, ext)

        # Chunk the document
        if ext in {'.md', '.markdown'}:
            chunks = self._chunk_markdown(content, relative_path)
        else:
            chunks = self._chunk_text(content, relative_path)

        # Convert to dictionaries
        result = []
        for chunk_content, metadata in chunks:
            summary = self._generate_summary(chunk_content, metadata)

            result.append({
                "project_id": project_id,
                "file_path": relative_path,
                "content": chunk_content,
                "start_line": metadata.get("start_line", 1),
                "end_line": metadata.get("end_line", 1),
                "doc_type": doc_type,
                "title": metadata.get("title", ""),
                "headings": metadata.get("headings", []),
                "summary": summary,
                "file_hash": file_hash
            })

        return result

    def _chunk_markdown(
        self,
        content: str,
        file_path: str
    ) -> List[tuple]:
        """
        Chunk markdown content by sections.

        Splits on headers while respecting chunk size limits.
        """
        chunks = []
        lines = content.split('\n')

        current_chunk = []
        current_headings = []
        current_title = ""
        start_line = 1
        current_size = 0

        for i, line in enumerate(lines, 1):
            # Check if this is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # Save previous chunk if it has content
                if current_chunk and current_size > 100:
                    chunk_content = '\n'.join(current_chunk)
                    chunks.append((chunk_content, {
                        "start_line": start_line,
                        "end_line": i - 1,
                        "title": current_title,
                        "headings": current_headings.copy()
                    }))
                    current_chunk = []
                    current_size = 0
                    start_line = i

                # Update heading context
                level = len(header_match.group(1))
                title = header_match.group(2).strip()

                # Maintain heading hierarchy
                current_headings = current_headings[:level-1]
                if len(current_headings) < level:
                    current_headings.extend([''] * (level - len(current_headings)))
                current_headings[level-1] = title
                current_title = title

            current_chunk.append(line)
            current_size += len(line)

            # Split if chunk is too large
            if current_size > self.chunk_size:
                chunk_content = '\n'.join(current_chunk)
                chunks.append((chunk_content, {
                    "start_line": start_line,
                    "end_line": i,
                    "title": current_title,
                    "headings": current_headings.copy()
                }))

                # Start new chunk with overlap
                overlap_lines = min(5, len(current_chunk) // 4)
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                current_size = sum(len(l) for l in current_chunk)
                start_line = i - overlap_lines + 1

        # Save final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content.strip()) > 50:  # Skip very small chunks
                chunks.append((chunk_content, {
                    "start_line": start_line,
                    "end_line": len(lines),
                    "title": current_title,
                    "headings": current_headings.copy()
                }))

        return chunks

    def _chunk_text(
        self,
        content: str,
        file_path: str
    ) -> List[tuple]:
        """Chunk plain text content by paragraphs."""
        chunks = []
        lines = content.split('\n')

        current_chunk = []
        start_line = 1
        current_size = 0

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)
            current_size += len(line)

            # Split on double newlines (paragraphs) or size limit
            if current_size > self.chunk_size or (line.strip() == '' and current_size > self.chunk_size // 2):
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    if len(chunk_content.strip()) > 50:
                        chunks.append((chunk_content, {
                            "start_line": start_line,
                            "end_line": i,
                            "title": "",
                            "headings": []
                        }))

                    overlap_lines = min(3, len(current_chunk) // 4)
                    current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                    current_size = sum(len(l) for l in current_chunk)
                    start_line = i - overlap_lines + 1

        # Save final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if len(chunk_content.strip()) > 50:
                chunks.append((chunk_content, {
                    "start_line": start_line,
                    "end_line": len(lines),
                    "title": "",
                    "headings": []
                }))

        return chunks

    def _detect_doc_type(self, file_path: str, ext: str) -> str:
        """Detect document type from file path and extension."""
        filename = os.path.basename(file_path).upper()

        if 'README' in filename:
            return 'readme'
        elif 'CONTRIBUTING' in filename:
            return 'contributing'
        elif 'CHANGELOG' in filename or 'HISTORY' in filename:
            return 'changelog'
        elif 'LICENSE' in filename:
            return 'license'
        elif 'API' in file_path.upper():
            return 'api-doc'
        elif 'GUIDE' in file_path.upper() or 'TUTORIAL' in file_path.upper():
            return 'guide'
        elif ext == '.rst':
            return 'restructuredtext'
        elif ext == '.adoc':
            return 'asciidoc'
        elif ext in {'.md', '.markdown'}:
            return 'markdown'
        else:
            return 'text'

    def _generate_summary(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate a summary for a documentation chunk."""
        title = metadata.get("title", "")
        headings = metadata.get("headings", [])

        # Build summary from headings
        heading_path = " > ".join(h for h in headings if h)

        # Extract first meaningful line
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        first_line = lines[0][:200] if lines else ""

        if title:
            summary = f"{title}"
            if heading_path and heading_path != title:
                summary += f" ({heading_path})"
        elif heading_path:
            summary = heading_path
        elif first_line:
            summary = first_line[:150]
        else:
            summary = "Documentation section"

        return summary

    async def _save_chunks_with_embeddings(
        self,
        project_id: str,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """Generate embeddings and save chunks to MongoDB."""
        saved_count = 0

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]

            # Prepare texts for embedding
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
                        doc_type=chunk["doc_type"],
                        title=chunk["title"],
                        headings=chunk["headings"],
                        summary=chunk["summary"],
                        file_hash=chunk["file_hash"]
                    )
                    saved_count += 1

                logger.debug(f"Saved doc batch {i // self.batch_size + 1}, total {saved_count} chunks")

            except Exception as e:
                logger.error(f"Failed to save doc batch: {e}")
                raise

        return saved_count


class DocumentationSearchService:
    """Service for semantic documentation search using MongoDB Atlas Vector Search."""

    def __init__(
        self,
        repository,  # MongoDBDocumentationRepository
        embedding_service: VoyageEmbeddingService
    ):
        """Initialize search service."""
        self.repository = repository
        self.embedding_service = embedding_service

    async def search(
        self,
        project_id: str,
        query: str,
        limit: int = 20,
        min_similarity: float = 0.0,
        doc_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documentation using natural language query.

        Args:
            project_id: Project ID
            query: Natural language search query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            doc_type: Optional doc type filter (readme, guide, api-doc, etc.)

        Returns:
            List of matching documentation chunks with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_query_embedding(query)

        # Build filters
        filters = {}
        if doc_type:
            filters["doc_type"] = doc_type

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
        """Get indexing statistics for a project."""
        return await self.repository.get_stats(project_id)

    async def get_indexed_files(self, project_id: str) -> List[str]:
        """Get list of all indexed documentation files."""
        return await self.repository.get_indexed_files(project_id)
