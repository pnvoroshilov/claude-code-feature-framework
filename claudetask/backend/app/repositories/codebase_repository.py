"""Codebase repository implementations for code chunk storage and vector search"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging
import hashlib

from .base import BaseRepository

logger = logging.getLogger(__name__)


class MongoDBCodebaseRepository(BaseRepository):
    """
    MongoDB implementation of codebase repository for semantic code search.

    Uses MongoDB Atlas Vector Search with voyage-3-large embeddings (1024d).
    Stores code chunks with metadata for intelligent code retrieval.

    Collection: codebase_chunks
    Index: codebase_vector_idx (must be created in Atlas)

    Document structure:
    {
        "_id": ObjectId,
        "project_id": str,           # Project identifier
        "file_path": str,            # Relative path from project root
        "content": str,              # Code chunk content
        "embedding": [float],        # 1024-dimensional vector (voyage-3-large)
        "start_line": int,           # Starting line number
        "end_line": int,             # Ending line number
        "language": str,             # Programming language
        "chunk_type": str,           # function, class, block, import, etc.
        "symbols": [str],            # Function names, class names, etc.
        "summary": str,              # AI-generated summary of the chunk
        "file_hash": str,            # Hash for change detection
        "indexed_at": datetime,      # When this chunk was indexed
        "metadata": dict             # Additional metadata
    }
    """

    COLLECTION_NAME = "codebase_chunks"
    VECTOR_INDEX_NAME = "codebase_vector_idx"

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB codebase repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve code chunk by ID from MongoDB."""
        from bson import ObjectId

        try:
            doc = await self._collection.find_one({"_id": ObjectId(id)})
            if doc:
                return self._doc_to_chunk(doc)
        except Exception as e:
            logger.error(f"Failed to get chunk by id {id}: {e}")

        return None

    async def create(self, entity: Any) -> str:
        """Create new code chunk in MongoDB."""
        doc = self._chunk_to_doc(entity)
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update code chunk in MongoDB."""
        from bson import ObjectId

        doc = self._chunk_to_doc(entity)
        chunk_id = entity.get("id") if isinstance(entity, dict) else entity.id

        await self._collection.update_one(
            {"_id": ObjectId(chunk_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete code chunk from MongoDB."""
        from bson import ObjectId

        await self._collection.delete_one({"_id": ObjectId(id)})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List code chunks from MongoDB."""
        query = {}

        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "file_path" in filters:
                query["file_path"] = filters["file_path"]
            if "language" in filters:
                query["language"] = filters["language"]
            if "chunk_type" in filters:
                query["chunk_type"] = filters["chunk_type"]

        cursor = (
            self._collection
            .find(query)
            .sort("file_path", 1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_chunk(doc) for doc in docs]

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count code chunks in MongoDB."""
        query = {}

        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "file_path" in filters:
                query["file_path"] = filters["file_path"]

        return await self._collection.count_documents(query)

    async def save_chunk(
        self,
        project_id: str,
        file_path: str,
        content: str,
        embedding: List[float],
        start_line: int,
        end_line: int,
        language: str,
        chunk_type: str,
        symbols: List[str],
        summary: str,
        file_hash: str
    ) -> str:
        """
        Save code chunk with voyage-3-large embedding.

        Uses upsert to handle re-indexing of existing chunks.

        Args:
            project_id: Project ID
            file_path: Relative file path
            content: Code chunk content
            embedding: 1024-dimensional vector (voyage-3-large)
            start_line: Starting line number
            end_line: Ending line number
            language: Programming language
            chunk_type: Type of chunk (function, class, etc.)
            symbols: List of symbol names in this chunk
            summary: AI-generated summary
            file_hash: Hash for change detection

        Returns:
            ID of saved chunk (ObjectId as string)
        """
        # Create deterministic chunk ID based on file path and line numbers
        chunk_key = f"{project_id}:{file_path}:{start_line}:{end_line}"
        chunk_id = hashlib.sha256(chunk_key.encode()).hexdigest()[:24]

        doc = {
            "chunk_id": chunk_id,
            "project_id": project_id,
            "file_path": file_path,
            "content": content,
            "embedding": embedding,
            "start_line": start_line,
            "end_line": end_line,
            "language": language,
            "chunk_type": chunk_type,
            "symbols": symbols,
            "summary": summary,
            "file_hash": file_hash,
            "indexed_at": datetime.utcnow()
        }

        # Upsert: update if exists, insert if not
        result = await self._collection.update_one(
            {"chunk_id": chunk_id, "project_id": project_id},
            {"$set": doc},
            upsert=True
        )

        return chunk_id

    async def delete_by_file(self, project_id: str, file_path: str) -> int:
        """
        Delete all chunks for a specific file.

        Used when re-indexing a file or when file is deleted.

        Args:
            project_id: Project ID
            file_path: Relative file path

        Returns:
            Number of deleted chunks
        """
        result = await self._collection.delete_many({
            "project_id": project_id,
            "file_path": file_path
        })

        logger.info(f"Deleted {result.deleted_count} chunks for {file_path}")
        return result.deleted_count

    async def delete_by_project(self, project_id: str) -> int:
        """
        Delete all chunks for a project.

        Used when re-indexing entire codebase.

        Args:
            project_id: Project ID

        Returns:
            Number of deleted chunks
        """
        result = await self._collection.delete_many({"project_id": project_id})
        logger.info(f"Deleted {result.deleted_count} chunks for project {project_id}")
        return result.deleted_count

    async def get_file_hashes(self, project_id: str) -> Dict[str, str]:
        """
        Get all file hashes for a project.

        Used for incremental indexing to detect changed files.

        Args:
            project_id: Project ID

        Returns:
            Dict mapping file_path to file_hash
        """
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$group": {
                "_id": "$file_path",
                "file_hash": {"$first": "$file_hash"}
            }}
        ]

        cursor = self._collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)

        return {doc["_id"]: doc["file_hash"] for doc in docs}

    async def vector_search(
        self,
        project_id: str,
        query_embedding: List[float],
        limit: int = 20,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using MongoDB Atlas Vector Search.

        Uses cosine similarity for comparing voyage-3-large embeddings (1024d).

        Args:
            project_id: Project ID to search within
            query_embedding: Query vector (1024d from voyage-3-large)
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0.0-1.0)
            filters: Optional metadata filters (language, chunk_type, file_path pattern)

        Returns:
            List of matching chunks with similarity scores

        Note:
            Requires MongoDB Atlas Vector Search index 'codebase_vector_idx' on 'embedding' field.
            Index must be created via Atlas UI with:
            - Field: embedding
            - Dimensions: 1024
            - Similarity: cosine
        """
        # Build pre-filter for vector search
        pre_filter = {"project_id": project_id}

        if filters:
            if "language" in filters:
                pre_filter["language"] = filters["language"]
            if "chunk_type" in filters:
                pre_filter["chunk_type"] = filters["chunk_type"]

        # Build aggregation pipeline for vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": min(limit * 10, 500),  # Fetch more candidates for better results
                    "limit": limit * 2,  # Get extra for filtering
                    "filter": pre_filter
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "chunk_id": 1,
                    "project_id": 1,
                    "file_path": 1,
                    "content": 1,
                    "start_line": 1,
                    "end_line": 1,
                    "language": 1,
                    "chunk_type": 1,
                    "symbols": 1,
                    "summary": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        # Add minimum similarity filter if specified
        if min_similarity > 0:
            pipeline.append({
                "$match": {"score": {"$gte": min_similarity}}
            })

        # Limit final results
        pipeline.append({"$limit": limit})

        try:
            cursor = self._collection.aggregate(pipeline)
            docs = await cursor.to_list(length=limit)

            # Deduplicate by file_path + line range
            seen = set()
            unique_results = []

            for doc in docs:
                key = (doc["file_path"], doc["start_line"], doc["end_line"])
                if key not in seen:
                    seen.add(key)
                    unique_results.append(self._doc_to_chunk(doc))

            logger.info(f"Vector search returned {len(unique_results)} unique results for project {project_id}")
            return unique_results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            # Return empty list on error (index might not exist yet)
            return []

    async def get_indexed_files(self, project_id: str) -> List[str]:
        """
        Get list of all indexed files for a project.

        Args:
            project_id: Project ID

        Returns:
            List of file paths
        """
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$group": {"_id": "$file_path"}},
            {"$sort": {"_id": 1}}
        ]

        cursor = self._collection.aggregate(pipeline)
        docs = await cursor.to_list(length=None)

        return [doc["_id"] for doc in docs]

    async def get_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get indexing statistics for a project.

        Args:
            project_id: Project ID

        Returns:
            Statistics dict with counts by language, chunk type, etc.
        """
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$facet": {
                "total": [{"$count": "count"}],
                "by_language": [
                    {"$group": {"_id": "$language", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "by_chunk_type": [
                    {"$group": {"_id": "$chunk_type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "files": [
                    {"$group": {"_id": "$file_path"}},
                    {"$count": "count"}
                ]
            }}
        ]

        cursor = self._collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        if not result:
            return {
                "total_chunks": 0,
                "total_files": 0,
                "by_language": {},
                "by_chunk_type": {}
            }

        data = result[0]

        return {
            "total_chunks": data["total"][0]["count"] if data["total"] else 0,
            "total_files": data["files"][0]["count"] if data["files"] else 0,
            "by_language": {item["_id"]: item["count"] for item in data["by_language"]},
            "by_chunk_type": {item["_id"]: item["count"] for item in data["by_chunk_type"]}
        }

    async def ensure_indexes(self):
        """
        Create regular MongoDB indexes for efficient queries.

        Note: Vector search index must be created separately in MongoDB Atlas UI.
        """
        # Compound index for project + file queries
        await self._collection.create_index([
            ("project_id", 1),
            ("file_path", 1)
        ])

        # Index for chunk lookup
        await self._collection.create_index([
            ("project_id", 1),
            ("chunk_id", 1)
        ], unique=True)

        # Index for language/type filtering
        await self._collection.create_index([
            ("project_id", 1),
            ("language", 1),
            ("chunk_type", 1)
        ])

        logger.info("Codebase indexes created")

    def _chunk_to_doc(self, chunk: Any) -> Dict[str, Any]:
        """Convert chunk to MongoDB document."""
        if isinstance(chunk, dict):
            return chunk

        return {
            "project_id": chunk.project_id,
            "file_path": chunk.file_path,
            "content": chunk.content,
            "embedding": chunk.embedding,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "language": chunk.language,
            "chunk_type": chunk.chunk_type,
            "symbols": chunk.symbols,
            "summary": chunk.summary,
            "file_hash": chunk.file_hash,
            "indexed_at": datetime.utcnow()
        }

    def _doc_to_chunk(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to chunk dict."""
        return {
            "id": str(doc.get("_id", "")),
            "chunk_id": doc.get("chunk_id"),
            "project_id": doc.get("project_id"),
            "file_path": doc.get("file_path"),
            "content": doc.get("content"),
            "start_line": doc.get("start_line"),
            "end_line": doc.get("end_line"),
            "language": doc.get("language"),
            "chunk_type": doc.get("chunk_type"),
            "symbols": doc.get("symbols", []),
            "summary": doc.get("summary"),
            "file_hash": doc.get("file_hash"),
            "indexed_at": doc.get("indexed_at"),
            "score": doc.get("score")  # Similarity score from vector search
        }
