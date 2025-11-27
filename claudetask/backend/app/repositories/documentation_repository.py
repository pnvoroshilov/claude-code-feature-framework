"""Documentation repository implementations for document chunk storage and vector search"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging
import hashlib

from .base import BaseRepository

logger = logging.getLogger(__name__)


class MongoDBDocumentationRepository(BaseRepository):
    """
    MongoDB implementation of documentation repository for semantic doc search.

    Uses MongoDB Atlas Vector Search with voyage-3-large embeddings (1024d).
    Stores documentation chunks with metadata for intelligent retrieval.

    Collection: documentation_chunks
    Index: documentation_vector_idx (must be created in Atlas)

    Document structure:
    {
        "_id": ObjectId,
        "project_id": str,           # Project identifier
        "file_path": str,            # Relative path from project root
        "content": str,              # Documentation chunk content
        "embedding": [float],        # 1024-dimensional vector (voyage-3-large)
        "start_line": int,           # Starting line number
        "end_line": int,             # Ending line number
        "doc_type": str,             # markdown, readme, api-doc, guide, etc.
        "title": str,                # Section title if available
        "headings": [str],           # Heading hierarchy
        "summary": str,              # AI-generated summary of the chunk
        "file_hash": str,            # Hash for change detection
        "indexed_at": datetime,      # When this chunk was indexed
        "metadata": dict             # Additional metadata
    }
    """

    COLLECTION_NAME = "documentation_chunks"
    VECTOR_INDEX_NAME = "documentation_vector_idx"

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB documentation repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve documentation chunk by ID from MongoDB."""
        from bson import ObjectId

        try:
            doc = await self._collection.find_one({"_id": ObjectId(id)})
            if doc:
                return self._doc_to_chunk(doc)
        except Exception as e:
            logger.error(f"Failed to get doc chunk by id {id}: {e}")

        return None

    async def create(self, entity: Any) -> str:
        """Create new documentation chunk in MongoDB."""
        doc = self._chunk_to_doc(entity)
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update documentation chunk in MongoDB."""
        from bson import ObjectId

        doc = self._chunk_to_doc(entity)
        chunk_id = entity.get("id") if isinstance(entity, dict) else entity.id

        await self._collection.update_one(
            {"_id": ObjectId(chunk_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete documentation chunk from MongoDB."""
        from bson import ObjectId

        await self._collection.delete_one({"_id": ObjectId(id)})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List documentation chunks from MongoDB."""
        query = {}
        if filters:
            query.update(filters)

        cursor = self._collection.find(query).skip(skip).limit(limit)
        return [self._doc_to_chunk(doc) async for doc in cursor]

    # Documentation-specific methods

    async def save_chunk(
        self,
        project_id: str,
        file_path: str,
        content: str,
        embedding: List[float],
        start_line: int,
        end_line: int,
        doc_type: str,
        title: Optional[str] = None,
        headings: Optional[List[str]] = None,
        summary: Optional[str] = None,
        file_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a documentation chunk with embedding.

        Args:
            project_id: Project identifier
            file_path: Relative path from project root
            content: Documentation chunk content
            embedding: 1024-dimensional voyage-3-large vector
            start_line: Starting line number
            end_line: Ending line number
            doc_type: Type of documentation (markdown, readme, guide, etc.)
            title: Section title if available
            headings: Heading hierarchy
            summary: AI-generated summary
            file_hash: Hash for change detection
            metadata: Additional metadata

        Returns:
            Inserted document ID
        """
        doc = {
            "project_id": project_id,
            "file_path": file_path,
            "content": content,
            "embedding": embedding,
            "start_line": start_line,
            "end_line": end_line,
            "doc_type": doc_type,
            "title": title or "",
            "headings": headings or [],
            "summary": summary or "",
            "file_hash": file_hash or hashlib.sha256(content.encode()).hexdigest(),
            "indexed_at": datetime.utcnow(),
            "metadata": metadata or {}
        }

        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def delete_by_project(self, project_id: str) -> int:
        """Delete all documentation chunks for a project."""
        result = await self._collection.delete_many({"project_id": project_id})
        return result.deleted_count

    async def delete_by_file(self, project_id: str, file_path: str) -> int:
        """Delete all chunks for a specific file."""
        result = await self._collection.delete_many({
            "project_id": project_id,
            "file_path": file_path
        })
        return result.deleted_count

    async def get_file_hashes(self, project_id: str) -> Dict[str, str]:
        """
        Get file hashes for all indexed documentation files.

        Returns dict mapping file_path to file_hash for change detection.
        """
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$group": {
                "_id": "$file_path",
                "hash": {"$first": "$file_hash"}
            }}
        ]

        result = {}
        async for doc in self._collection.aggregate(pipeline):
            result[doc["_id"]] = doc["hash"]

        return result

    async def vector_search(
        self,
        project_id: str,
        query_embedding: List[float],
        limit: int = 20,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search for documentation.

        Uses MongoDB Atlas Vector Search with cosine similarity.

        Args:
            project_id: Project to search within
            query_embedding: 1024-dimensional query vector
            limit: Maximum results to return
            min_similarity: Minimum similarity threshold (0.0-1.0)
            filters: Additional filters (doc_type, etc.)

        Returns:
            List of matching documentation chunks with similarity scores
        """
        # Build filter for $vectorSearch
        vector_filter = {"project_id": project_id}
        if filters:
            vector_filter.update(filters)

        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit,
                    "filter": vector_filter
                }
            },
            {
                "$project": {
                    "file_path": 1,
                    "content": 1,
                    "start_line": 1,
                    "end_line": 1,
                    "doc_type": 1,
                    "title": 1,
                    "headings": 1,
                    "summary": 1,
                    "indexed_at": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        results = []
        async for doc in self._collection.aggregate(pipeline):
            score = doc.pop("score", 0)
            if score >= min_similarity:
                doc["similarity_score"] = score
                doc["_id"] = str(doc["_id"])
                results.append(doc)

        return results

    async def get_stats(self, project_id: str) -> Dict[str, Any]:
        """Get indexing statistics for a project."""
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$group": {
                "_id": None,
                "total_chunks": {"$sum": 1},
                "unique_files": {"$addToSet": "$file_path"},
                "doc_types": {"$addToSet": "$doc_type"},
                "last_indexed": {"$max": "$indexed_at"}
            }}
        ]

        async for doc in self._collection.aggregate(pipeline):
            return {
                "total_chunks": doc["total_chunks"],
                "unique_files": len(doc["unique_files"]),
                "doc_types": doc["doc_types"],
                "last_indexed": doc["last_indexed"].isoformat() if doc["last_indexed"] else None
            }

        return {
            "total_chunks": 0,
            "unique_files": 0,
            "doc_types": [],
            "last_indexed": None
        }

    async def get_indexed_files(self, project_id: str) -> List[str]:
        """Get list of all indexed documentation files."""
        files = await self._collection.distinct("file_path", {"project_id": project_id})
        return sorted(files)

    async def ensure_indexes(self):
        """Create regular MongoDB indexes for efficient queries."""
        # Compound index for project + file lookups
        await self._collection.create_index([
            ("project_id", 1),
            ("file_path", 1)
        ])

        # Index for doc_type filtering
        await self._collection.create_index([
            ("project_id", 1),
            ("doc_type", 1)
        ])

        # Index for file hash lookups (change detection)
        await self._collection.create_index([
            ("project_id", 1),
            ("file_hash", 1)
        ])

        logger.info(f"Created indexes for {self.COLLECTION_NAME}")

    def _doc_to_chunk(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to chunk dict."""
        return {
            "id": str(doc["_id"]),
            "project_id": doc.get("project_id"),
            "file_path": doc.get("file_path"),
            "content": doc.get("content"),
            "start_line": doc.get("start_line"),
            "end_line": doc.get("end_line"),
            "doc_type": doc.get("doc_type"),
            "title": doc.get("title"),
            "headings": doc.get("headings", []),
            "summary": doc.get("summary"),
            "file_hash": doc.get("file_hash"),
            "indexed_at": doc.get("indexed_at"),
            "similarity_score": doc.get("similarity_score")
        }

    def _chunk_to_doc(self, entity: Any) -> Dict[str, Any]:
        """Convert chunk entity to MongoDB document."""
        if isinstance(entity, dict):
            return {k: v for k, v in entity.items() if k != "id" and k != "_id"}
        return {}
