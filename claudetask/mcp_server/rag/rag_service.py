"""
RAG Service - Retrieval-Augmented Generation for ClaudeTask Framework

This service provides semantic search capabilities across:
1. Codebase (main repository code chunks)
2. Task history (completed tasks with analysis and outcomes)

Architecture:
- ChromaDB: Vector database for embeddings storage
- Sentence Transformers: Embedding generation (all-MiniLM-L6-v2)
- Semantic chunking: Intelligent code splitting with summaries
"""

import os
import logging
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import git


logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """Configuration for RAG service"""
    chromadb_path: str = ".claudetask/chromadb"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500  # tokens
    chunk_overlap: int = 50  # tokens
    top_k_default: int = 10
    relevance_threshold: float = 0.7
    enable_caching: bool = True
    cache_size: int = 1000


@dataclass
class CodeChunk:
    """Represents a semantic code chunk"""
    chunk_id: str
    repository: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    summary: str
    language: str
    chunk_type: str  # function, class, block, import, etc.
    symbols: List[str]  # function names, class names, etc.


@dataclass
class RAGSearchResult:
    """Search result from RAG system"""
    code_chunks: List[CodeChunk]
    similar_tasks: List[Dict[str, Any]]
    file_suggestions: List[str]
    confidence_score: float
    query_time_ms: float


class RAGService:
    """
    Main RAG service for semantic search across codebase and tasks.

    Features:
    - Semantic code search with ChromaDB
    - Task similarity matching
    - Automatic context assembly for task analysis
    - Incremental indexing on code changes
    """

    def __init__(self, config: RAGConfig):
        """Initialize RAG service with configuration"""
        self.config = config
        self.client: Optional[chromadb.Client] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.codebase_collection = None
        self.tasks_collection = None

        logger.info(f"RAG Service initializing with model: {config.embedding_model}")

    async def initialize(self):
        """
        Initialize ChromaDB and embedding model.
        Called on MCP server startup.
        """
        try:
            # Initialize ChromaDB client (new API)
            chromadb_path = Path(self.config.chromadb_path)
            chromadb_path.mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(path=str(chromadb_path))

            logger.info(f"ChromaDB initialized at {chromadb_path}")

            # Load or create collections
            await self._initialize_collections()

            # Load embedding model
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info("Embedding model loaded successfully")

            logger.info("RAG Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise

    async def _initialize_collections(self):
        """Initialize or load ChromaDB collections"""
        try:
            # Codebase collection
            self.codebase_collection = self.client.get_or_create_collection(
                name="codebase_chunks",
                metadata={
                    "description": "Semantic code chunks from repository",
                    "embedding_model": self.config.embedding_model
                }
            )

            # Tasks collection
            self.tasks_collection = self.client.get_or_create_collection(
                name="task_history",
                metadata={
                    "description": "Completed tasks with analysis and outcomes",
                    "embedding_model": self.config.embedding_model
                }
            )

            logger.info("Collections initialized")
            logger.info(f"Codebase chunks: {self.codebase_collection.count()}")
            logger.info(f"Tasks indexed: {self.tasks_collection.count()}")

        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise

    async def index_exists(self) -> bool:
        """Check if RAG index already exists"""
        try:
            if self.codebase_collection is None:
                return False
            return self.codebase_collection.count() > 0
        except:
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
            filters: Optional metadata filters (file_type, repository, etc.)

        Returns:
            List of relevant code chunks ranked by relevance
        """
        if not self.embedding_model:
            raise RuntimeError("RAG service not initialized")

        top_k = top_k or self.config.top_k_default

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search ChromaDB
            results = self.codebase_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters if filters else {}
            )

            # Convert to CodeChunk objects with deduplication
            code_chunks = []
            seen_chunks = set()  # Track unique chunks by (file_path, start_line, end_line)

            if results and results['ids'] and len(results['ids']) > 0:
                ids = results['ids'][0]
                metadatas = results['metadatas'][0]
                documents = results['documents'][0]

                for i in range(len(ids)):
                    metadata = metadatas[i]

                    # Create unique identifier for deduplication
                    chunk_key = (
                        metadata.get('file_path', ''),
                        metadata.get('start_line', 0),
                        metadata.get('end_line', 0)
                    )

                    # Skip if we've already seen this chunk
                    if chunk_key in seen_chunks:
                        logger.debug(f"Skipping duplicate chunk: {chunk_key}")
                        continue

                    seen_chunks.add(chunk_key)

                    chunk = CodeChunk(
                        chunk_id=ids[i],
                        repository="main",
                        file_path=metadata.get('file_path', ''),
                        start_line=metadata.get('start_line', 0),
                        end_line=metadata.get('end_line', 0),
                        content=documents[i],
                        summary=metadata.get('summary', ''),
                        language=metadata.get('language', 'unknown'),
                        chunk_type=metadata.get('chunk_type', 'unknown'),
                        symbols=metadata.get('symbols', '').split(',') if metadata.get('symbols') else []
                    )
                    code_chunks.append(chunk)

            logger.info(f"Code search returned {len(code_chunks)} results")
            return code_chunks

        except Exception as e:
            logger.error(f"Codebase search failed: {e}")
            return []

    async def find_similar_tasks(
        self,
        task_description: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar historical tasks.

        Args:
            task_description: Description of current task
            top_k: Number of similar tasks to return

        Returns:
            List of similar tasks with their details
        """
        if not self.embedding_model:
            raise RuntimeError("RAG service not initialized")

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(task_description).tolist()

            # Search tasks collection
            results = self.tasks_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # Convert to task dictionaries with deduplication
            similar_tasks = []
            seen_tasks = set()  # Track unique tasks by task_id

            if results and results['ids'] and len(results['ids']) > 0:
                ids = results['ids'][0]
                metadatas = results['metadatas'][0]
                documents = results['documents'][0]
                distances = results.get('distances', [[]])[0] if 'distances' in results else []

                for i in range(len(ids)):
                    metadata = metadatas[i]
                    task_id = metadata.get('task_id')

                    # Skip if we've already seen this task
                    if task_id in seen_tasks:
                        logger.debug(f"Skipping duplicate task: {task_id}")
                        continue

                    seen_tasks.add(task_id)

                    # Convert distance to similarity (1 - distance for L2, higher is better)
                    similarity = 1.0 - distances[i] if i < len(distances) else 0.0

                    task = {
                        'task_id': task_id,
                        'title': metadata.get('title', ''),
                        'task_type': metadata.get('task_type', ''),
                        'priority': metadata.get('priority', ''),
                        'status': metadata.get('status', ''),
                        'content': documents[i],
                        'similarity': similarity
                    }
                    similar_tasks.append(task)

            logger.info(f"Found {len(similar_tasks)} similar tasks")
            return similar_tasks

        except Exception as e:
            logger.error(f"Task similarity search failed: {e}")
            return []

    async def analyze_task_context(
        self,
        task_description: str
    ) -> RAGSearchResult:
        """
        Comprehensive context analysis for a task.
        Combines code search and task similarity.

        Args:
            task_description: Full task description

        Returns:
            RAGSearchResult with all relevant context
        """
        import time
        start_time = time.time()

        try:
            # Search codebase
            code_chunks = await self.search_codebase(task_description)

            # Find similar tasks
            similar_tasks = await self.find_similar_tasks(task_description)

            # Extract file suggestions from chunks
            file_suggestions = list(set([
                chunk.file_path for chunk in code_chunks
            ]))[:10]

            # Calculate confidence score
            confidence_score = self._calculate_confidence(code_chunks, similar_tasks)

            query_time_ms = (time.time() - start_time) * 1000

            return RAGSearchResult(
                code_chunks=code_chunks,
                similar_tasks=similar_tasks,
                file_suggestions=file_suggestions,
                confidence_score=confidence_score,
                query_time_ms=query_time_ms
            )

        except Exception as e:
            logger.error(f"Task context analysis failed: {e}")
            # Return empty result on error
            return RAGSearchResult(
                code_chunks=[],
                similar_tasks=[],
                file_suggestions=[],
                confidence_score=0.0,
                query_time_ms=0.0
            )

    def _calculate_confidence(
        self,
        code_chunks: List[CodeChunk],
        similar_tasks: List[Dict]
    ) -> float:
        """Calculate confidence score based on search results quality"""
        if not code_chunks and not similar_tasks:
            return 0.0

        # Simple confidence calculation
        # TODO: Implement more sophisticated scoring
        code_score = min(len(code_chunks) / 10.0, 1.0)
        task_score = min(len(similar_tasks) / 5.0, 1.0)

        return (code_score + task_score) / 2.0

    async def index_codebase(self, repo_path: str):
        """
        Index entire codebase.
        Called on first RAG initialization.

        Args:
            repo_path: Path to repository root
        """
        logger.info(f"Starting codebase indexing from {repo_path}")

        from chunking import GenericChunker
        import os

        chunker = GenericChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        # Supported file extensions
        supported_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.cs', '.go', '.rs', '.cpp', '.c',
            '.rb', '.php', '.swift', '.kt'
        }

        # Directories to skip
        skip_dirs = {
            'node_modules', 'venv', '__pycache__', '.git',
            'dist', 'build', '.next', 'target', 'bin', 'obj',
            '.claudetask', 'worktrees'
        }

        total_chunks = 0
        indexed_files = 0

        try:
            # Walk through repository
            for root, dirs, files in os.walk(repo_path):
                # Remove skip directories from dirs list (modifies in-place)
                dirs[:] = [d for d in dirs if d not in skip_dirs]

                for file in files:
                    # Check file extension
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in supported_extensions:
                        continue

                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)

                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Detect language
                        language = self._detect_language(ext)

                        # Chunk the file
                        chunks = chunker.chunk_code(content, relative_path, language)

                        # Index each chunk
                        for chunk_content, metadata in chunks:
                            # Generate summary
                            summary = chunker.generate_summary(chunk_content, metadata)

                            # Create embedding
                            embedding = self.embedding_model.encode(
                                f"{summary}\n\n{chunk_content}"
                            ).tolist()

                            # Generate deterministic ID based on file path and line numbers
                            chunk_id = f"{metadata.file_path}:{metadata.start_line}:{metadata.end_line}"

                            # Upsert to ChromaDB (replaces if ID exists, adds if new)
                            self.codebase_collection.upsert(
                                ids=[chunk_id],
                                embeddings=[embedding],
                                documents=[chunk_content],
                                metadatas=[{
                                    'file_path': metadata.file_path,
                                    'language': metadata.language,
                                    'start_line': metadata.start_line,
                                    'end_line': metadata.end_line,
                                    'chunk_type': metadata.chunk_type,
                                    'summary': summary,
                                    'symbols': ','.join(metadata.symbols) if metadata.symbols else ''
                                }]
                            )

                            total_chunks += 1

                        indexed_files += 1

                        if indexed_files % 10 == 0:
                            logger.info(f"Indexed {indexed_files} files, {total_chunks} chunks")

                    except Exception as e:
                        logger.warning(f"Failed to index {file_path}: {e}")
                        continue

            logger.info(f"Codebase indexing complete: {indexed_files} files, {total_chunks} chunks")

        except Exception as e:
            logger.error(f"Codebase indexing failed: {e}")
            raise

    async def index_files(self, file_paths: List[str], repo_path: str):
        """
        Index specific files (or re-index existing files).
        Useful for updating index after file modifications.

        Args:
            file_paths: List of file paths (absolute or relative to repo_path)
            repo_path: Path to repository root
        """
        logger.info(f"Starting indexing of {len(file_paths)} files")

        from chunking import GenericChunker
        import os

        chunker = GenericChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        # Supported file extensions
        supported_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.cs', '.go', '.rs', '.cpp', '.c',
            '.rb', '.php', '.swift', '.kt'
        }

        total_chunks = 0
        indexed_files = 0
        skipped_files = 0

        try:
            for file_path in file_paths:
                # Convert to absolute path if needed
                if not os.path.isabs(file_path):
                    abs_path = os.path.join(repo_path, file_path)
                else:
                    abs_path = file_path

                # Check if file exists
                if not os.path.exists(abs_path):
                    logger.warning(f"File not found: {abs_path}")
                    skipped_files += 1
                    continue

                # Check file extension
                ext = os.path.splitext(abs_path)[1].lower()
                if ext not in supported_extensions:
                    logger.warning(f"Unsupported file type: {abs_path} (extension: {ext})")
                    skipped_files += 1
                    continue

                relative_path = os.path.relpath(abs_path, repo_path)

                try:
                    # Remove existing chunks for this file before re-indexing
                    existing = self.codebase_collection.get(
                        where={"file_path": relative_path}
                    )
                    if existing and existing['ids']:
                        logger.info(f"Removing {len(existing['ids'])} existing chunks for {relative_path}")
                        self.codebase_collection.delete(ids=existing['ids'])

                    # Read file content
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Detect language
                    language = self._detect_language(ext)

                    # Chunk the file
                    chunks = chunker.chunk_code(content, relative_path, language)

                    # Index each chunk
                    file_chunks = 0
                    for chunk_content, metadata in chunks:
                        # Generate summary
                        summary = chunker.generate_summary(chunk_content, metadata)

                        # Create embedding
                        embedding = self.embedding_model.encode(
                            f"{summary}\n\n{chunk_content}"
                        ).tolist()

                        # Generate deterministic ID based on file path and line numbers
                        chunk_id = f"{metadata.file_path}:{metadata.start_line}:{metadata.end_line}"

                        # Upsert to ChromaDB (replaces if ID exists, adds if new)
                        self.codebase_collection.upsert(
                            ids=[chunk_id],
                            embeddings=[embedding],
                            documents=[chunk_content],
                            metadatas=[{
                                'file_path': metadata.file_path,
                                'language': metadata.language,
                                'start_line': metadata.start_line,
                                'end_line': metadata.end_line,
                                'chunk_type': metadata.chunk_type,
                                'summary': summary,
                                'symbols': ','.join(metadata.symbols) if metadata.symbols else ''
                            }]
                        )

                        file_chunks += 1
                        total_chunks += 1

                    indexed_files += 1
                    logger.info(f"Indexed {relative_path}: {file_chunks} chunks")

                except Exception as e:
                    logger.error(f"Failed to index {abs_path}: {e}")
                    skipped_files += 1
                    continue

            logger.info(f"File indexing complete: {indexed_files} indexed, {skipped_files} skipped, {total_chunks} total chunks")

            return {
                'indexed_files': indexed_files,
                'skipped_files': skipped_files,
                'total_chunks': total_chunks
            }

        except Exception as e:
            logger.error(f"File indexing failed: {e}")
            raise

    def _detect_language(self, ext: str) -> str:
        """Detect programming language from file extension"""
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
            '.kt': 'kotlin'
        }
        return language_map.get(ext.lower(), 'unknown')

    async def index_task(self, task: Dict[str, Any]):
        """
        Index a completed task (idempotent - replaces existing entry).
        Called when task status changes to Done.

        Args:
            task: Task dictionary with all details
        """
        task_id = task.get('id')
        logger.info(f"Indexing task #{task_id}")

        try:
            # Prepare task text for embedding (include stage results if available)
            stage_results = task.get('cumulative_results', '')

            task_text = f"""
Title: {task.get('title', '')}
Type: {task.get('task_type', '')}
Priority: {task.get('priority', '')}
Description: {task.get('description', '')}
Analysis: {task.get('analysis', '')}

Stage Results:
{stage_results}
"""

            # Create embedding
            embedding = self.embedding_model.encode(task_text).tolist()

            # Use deterministic ID for idempotent indexing
            chunk_id = f"task_{task_id}"

            # Delete existing entry if present (to enable re-indexing)
            try:
                existing = self.tasks_collection.get(ids=[chunk_id])
                if existing and existing['ids']:
                    logger.info(f"Removing existing index for task #{task_id}")
                    self.tasks_collection.delete(ids=[chunk_id])
            except Exception as e:
                # Collection might be empty or ID doesn't exist - this is fine
                logger.debug(f"No existing entry for task #{task_id}: {e}")

            # Upsert to ChromaDB (replaces if task already indexed)
            self.tasks_collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[task_text],
                metadatas=[{
                    'task_id': task_id,
                    'title': task.get('title', ''),
                    'task_type': task.get('task_type', ''),
                    'priority': task.get('priority', ''),
                    'status': task.get('status', ''),
                }]
            )

            logger.info(f"Task #{task_id} indexed successfully")

        except Exception as e:
            logger.error(f"Failed to index task #{task_id}: {e}")
            raise

    async def update_index_incremental(self, repo_path: str):
        """
        Incrementally update index for changed files.
        Called on MCP startup if index exists or after merge to main.

        Args:
            repo_path: Path to repository root
        """
        logger.info(f"Checking for index updates in {repo_path}")

        import os
        import hashlib
        from pathlib import Path

        # Load index metadata (tracks file hashes)
        metadata_path = Path(self.config.chromadb_path).parent / "index_metadata.json"

        # Load existing metadata
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                'last_indexed': None,
                'file_hashes': {}
            }

        updated_files = []
        new_files = []
        deleted_chunks = 0

        from chunking import GenericChunker

        chunker = GenericChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        supported_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.cs', '.go', '.rs', '.cpp', '.c',
            '.rb', '.php', '.swift', '.kt'
        }

        skip_dirs = {
            'node_modules', 'venv', '__pycache__', '.git',
            'dist', 'build', '.next', 'target', 'bin', 'obj',
            '.claudetask', 'worktrees'
        }

        try:
            # Walk through repository
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in skip_dirs]

                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in supported_extensions:
                        continue

                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)

                    # Calculate current file hash
                    try:
                        with open(file_path, 'rb') as f:
                            current_hash = hashlib.sha256(f.read()).hexdigest()
                    except:
                        continue

                    # Check if file changed
                    stored_hash = metadata['file_hashes'].get(relative_path)

                    if stored_hash == current_hash:
                        # File unchanged, skip
                        continue

                    # File is new or modified
                    if stored_hash is None:
                        new_files.append(relative_path)
                    else:
                        updated_files.append(relative_path)

                    # Delete old chunks for this file
                    try:
                        results = self.codebase_collection.get(
                            where={"file_path": relative_path}
                        )
                        if results and results['ids']:
                            self.codebase_collection.delete(ids=results['ids'])
                            deleted_chunks += len(results['ids'])
                    except Exception as e:
                        logger.warning(f"Failed to delete old chunks for {relative_path}: {e}")

                    # Re-index file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        language = self._detect_language(ext)
                        chunks = chunker.chunk_code(content, relative_path, language)

                        for chunk_content, chunk_metadata in chunks:
                            summary = chunker.generate_summary(chunk_content, chunk_metadata)
                            embedding = self.embedding_model.encode(
                                f"{summary}\n\n{chunk_content}"
                            ).tolist()

                            # Generate deterministic ID based on file path and line numbers
                            chunk_id = f"{chunk_metadata.file_path}:{chunk_metadata.start_line}:{chunk_metadata.end_line}"

                            self.codebase_collection.upsert(
                                ids=[chunk_id],
                                embeddings=[embedding],
                                documents=[chunk_content],
                                metadatas=[{
                                    'file_path': chunk_metadata.file_path,
                                    'language': chunk_metadata.language,
                                    'start_line': chunk_metadata.start_line,
                                    'end_line': chunk_metadata.end_line,
                                    'chunk_type': chunk_metadata.chunk_type,
                                    'summary': summary,
                                    'symbols': ','.join(chunk_metadata.symbols) if chunk_metadata.symbols else ''
                                }]
                            )

                        # Update metadata
                        metadata['file_hashes'][relative_path] = current_hash

                    except Exception as e:
                        logger.warning(f"Failed to re-index {relative_path}: {e}")

            # Save updated metadata
            import json
            from datetime import datetime
            metadata['last_indexed'] = datetime.now().isoformat()

            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Incremental update complete: {len(new_files)} new files, "
                       f"{len(updated_files)} updated files, {deleted_chunks} chunks deleted")

        except Exception as e:
            logger.error(f"Incremental indexing failed: {e}")
            raise

    async def reindex_merge_commit(self, repo_path: str, merge_commit_sha: Optional[str] = None):
        """
        Reindex only files changed in the merge commit.

        This is more efficient than full incremental update when we know
        exactly which files were merged.

        Args:
            repo_path: Path to git repository
            merge_commit_sha: SHA of merge commit (default: HEAD)
        """
        try:
            repo = git.Repo(repo_path)

            # Get merge commit (default to HEAD)
            commit = repo.head.commit if merge_commit_sha is None else repo.commit(merge_commit_sha)

            # Get changed files from merge commit
            # Compare with first parent to see what was merged
            if len(commit.parents) < 2:
                logger.warning(f"Commit {commit.hexsha} is not a merge commit, using regular diff")
                parent = commit.parents[0] if commit.parents else None
            else:
                # This is a merge commit - compare with first parent (main branch)
                parent = commit.parents[0]

            changed_files: Set[str] = set()

            if parent:
                # Get diff between parent and merge commit
                diffs = parent.diff(commit)

                for diff in diffs:
                    # Get file paths from both sides of diff
                    if diff.a_path:
                        changed_files.add(diff.a_path)
                    if diff.b_path and diff.b_path != diff.a_path:
                        changed_files.add(diff.b_path)
            else:
                # No parent - index all files in commit
                for item in commit.tree.traverse():
                    if item.type == 'blob':  # It's a file
                        changed_files.add(item.path)

            logger.info(f"Found {len(changed_files)} changed files in merge commit {commit.hexsha[:8]}")

            # Filter to only supported file types
            supported_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java',
                                   '.cs', '.go', '.rs', '.cpp', '.c', '.rb', '.php', '.swift', '.kt'}

            files_to_reindex = []
            for file_path in changed_files:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in supported_extensions:
                    full_path = os.path.join(repo_path, file_path)
                    if os.path.exists(full_path):
                        files_to_reindex.append(file_path)
                    else:
                        # File was deleted - remove from index
                        await self._remove_file_chunks(file_path)
                        logger.info(f"Removed deleted file from index: {file_path}")

            if not files_to_reindex:
                logger.info("No supported code files to reindex")
                return

            logger.info(f"Reindexing {len(files_to_reindex)} files: {', '.join(files_to_reindex[:5])}{'...' if len(files_to_reindex) > 5 else ''}")

            # Reindex each changed file
            from chunking import GenericChunker
            chunker = GenericChunker(chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap)

            for relative_path in files_to_reindex:
                file_path = os.path.join(repo_path, relative_path)

                try:
                    # Remove old chunks for this file
                    await self._remove_file_chunks(relative_path)

                    # Read and re-index file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    language = self._detect_language(relative_path)
                    chunks = chunker.chunk_code(content, relative_path, language)

                    # Add new chunks
                    for chunk_content, chunk_metadata in chunks:
                        summary = chunker.generate_summary(chunk_content, chunk_metadata)

                        # Generate embedding
                        embedding = self.embedding_model.encode(f"{summary}\n\n{chunk_content}").tolist()

                        # Store in ChromaDB with deterministic ID
                        chunk_id = f"{chunk_metadata.file_path}:{chunk_metadata.start_line}:{chunk_metadata.end_line}"

                        self.codebase_collection.upsert(
                            ids=[chunk_id],
                            embeddings=[embedding],
                            documents=[chunk_content],
                            metadatas=[{
                                'file_path': chunk_metadata.file_path,
                                'language': chunk_metadata.language,
                                'start_line': chunk_metadata.start_line,
                                'end_line': chunk_metadata.end_line,
                                'chunk_type': chunk_metadata.chunk_type,
                                'summary': summary,
                                'symbols': ','.join(chunk_metadata.symbols) if chunk_metadata.symbols else ''
                            }]
                        )

                    logger.info(f"Reindexed {relative_path}: {len(chunks)} chunks")

                except Exception as e:
                    logger.warning(f"Failed to reindex {relative_path}: {e}")

            logger.info(f"Merge commit reindex complete: {len(files_to_reindex)} files updated")

        except Exception as e:
            logger.error(f"Merge commit reindexing failed: {e}")
            raise

    async def _remove_file_chunks(self, file_path: str):
        """Remove all chunks for a specific file from the index"""
        try:
            # Get all chunks for this file
            existing = self.codebase_collection.get(
                where={"file_path": file_path}
            )

            if existing and existing['ids']:
                # Delete all chunks for this file
                self.codebase_collection.delete(ids=existing['ids'])
                logger.debug(f"Removed {len(existing['ids'])} chunks for {file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove chunks for {file_path}: {e}")

    # ========================
    # Memory Management Methods
    # ========================

    async def initialize_memory_collection(self, project_id: str):
        """Initialize or get memory collection for a project"""
        try:
            collection_name = f"memory_{project_id[:8]}"  # Use first 8 chars of UUID

            self.memory_collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "type": "conversation_memory",
                    "project_id": project_id,
                    "embedding_model": self.config.embedding_model
                }
            )

            logger.info(f"Memory collection initialized for project {project_id[:8]}")
            return self.memory_collection

        except Exception as e:
            logger.error(f"Failed to initialize memory collection: {e}")
            raise

    async def index_conversation_message(
        self,
        project_id: str,
        message_id: int,
        content: str,
        metadata: dict
    ):
        """Index a conversation message for RAG search"""
        try:
            # Ensure collection exists
            if not hasattr(self, 'memory_collection') or self.memory_collection is None:
                await self.initialize_memory_collection(project_id)

            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()

            # Ensure metadata includes project_id (required for filtering in search)
            # Filter out None values as ChromaDB doesn't accept them
            full_metadata = {"project_id": project_id}
            for key, value in metadata.items():
                if value is not None:
                    full_metadata[key] = value

            # Add to collection
            self.memory_collection.add(
                ids=[f"msg_{message_id}"],
                documents=[content],
                embeddings=[embedding],
                metadatas=[full_metadata]
            )

            logger.info(f"Indexed message {message_id} for project {project_id[:8]} in collection {self.memory_collection.name}")

        except Exception as e:
            logger.error(f"Failed to index message {message_id}: {e}")

    async def search_memories(
        self,
        project_id: str,
        query: str,
        limit: int = 20,
        filters: Optional[dict] = None
    ) -> List[dict]:
        """Search project memories using semantic search"""
        try:
            # Ensure collection exists
            collection_name = f"memory_{project_id[:8]}"

            # Try to get existing collection
            try:
                memory_collection = self.client.get_collection(collection_name)
            except:
                # Collection doesn't exist yet
                logger.info(f"No memory collection found for project {project_id[:8]}")
                return []

            # Check collection count
            collection_count = memory_collection.count()
            logger.info(f"Memory collection {collection_name} has {collection_count} entries")

            if collection_count == 0:
                logger.info(f"No memories indexed yet for project {project_id[:8]}")
                return []

            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Build where clause - always filter by project_id
            where_clause = {"project_id": project_id}
            if filters:
                where_clause = {**filters, "project_id": project_id}

            logger.info(f"Searching with where_clause: {where_clause}")

            # Perform search
            results = memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause
            )

            # Format results
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': 1 - results['distances'][0][i] if results['distances'] else 0  # Convert distance to similarity
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []

    async def get_memory_stats(self, project_id: str) -> dict:
        """Get statistics about memory collection for a project"""
        try:
            collection_name = f"memory_{project_id[:8]}"

            try:
                memory_collection = self.client.get_collection(collection_name)
                count = memory_collection.count()

                return {
                    "total_messages": count,
                    "collection_name": collection_name,
                    "status": "active"
                }
            except:
                return {
                    "total_messages": 0,
                    "collection_name": collection_name,
                    "status": "not_initialized"
                }

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "total_messages": 0,
                "error": str(e)
            }

    async def rebuild_memory_index(self, project_id: str, messages: List[dict]):
        """Rebuild the entire memory index for a project"""
        try:
            collection_name = f"memory_{project_id[:8]}"

            # Delete existing collection if it exists
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted existing memory collection for project {project_id[:8]}")
            except:
                pass

            # Create new collection
            await self.initialize_memory_collection(project_id)

            # Index all messages
            for msg in messages:
                await self.index_conversation_message(
                    project_id=project_id,
                    message_id=msg['id'],
                    content=msg['content'],
                    metadata={
                        "message_type": msg.get('message_type', 'unknown'),
                        "timestamp": msg.get('timestamp', ''),
                        "task_id": msg.get('task_id'),
                        "session_id": msg.get('session_id')
                    }
                )

            logger.info(f"Rebuilt memory index with {len(messages)} messages for project {project_id[:8]}")

        except Exception as e:
            logger.error(f"Failed to rebuild memory index: {e}")
            raise
