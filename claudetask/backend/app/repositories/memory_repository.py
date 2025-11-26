"""Memory repository implementations for conversation storage and vector search"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from .base import BaseRepository


class SQLiteMemoryRepository(BaseRepository):
    """
    SQLite implementation of conversation memory repository.

    Uses ChromaDB for vector search with all-MiniLM-L6-v2 embeddings (384d).
    This implementation maintains backward compatibility with local storage.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize SQLite memory repository.

        Args:
            db: SQLAlchemy async session
        """
        self._db = db

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation message by ID from SQLite."""
        query = text(
            "SELECT * FROM conversation_memory WHERE id = :id"
        )
        result = await self._db.execute(query, {"id": int(id)})
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return None

    async def create(self, entity: Any) -> str:
        """Create new conversation message in SQLite."""
        # This would use ChromaDB for actual storage
        # For now, placeholder implementation
        pass

    async def update(self, entity: Any) -> None:
        """Update conversation message in SQLite."""
        pass

    async def delete(self, id: str) -> None:
        """Delete conversation message from SQLite."""
        query = text("DELETE FROM conversation_memory WHERE id = :id")
        await self._db.execute(query, {"id": int(id)})
        await self._db.commit()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List conversation messages from SQLite."""
        query_str = "SELECT * FROM conversation_memory WHERE 1=1"
        params = {}

        if filters:
            if "project_id" in filters:
                query_str += " AND project_id = :project_id"
                params["project_id"] = filters["project_id"]
            if "session_id" in filters:
                query_str += " AND session_id = :session_id"
                params["session_id"] = filters["session_id"]

        query_str += " ORDER BY timestamp DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip

        result = await self._db.execute(text(query_str), params)
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count conversation messages in SQLite."""
        query_str = "SELECT COUNT(*) as count FROM conversation_memory WHERE 1=1"
        params = {}

        if filters:
            if "project_id" in filters:
                query_str += " AND project_id = :project_id"
                params["project_id"] = filters["project_id"]

        result = await self._db.execute(text(query_str), params)
        row = result.fetchone()
        return row[0] if row else 0

    async def save_message(
        self,
        project_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save conversation message with embedding.

        For SQLite mode, this delegates to ChromaDB.

        Args:
            project_id: Project ID
            content: Message content
            embedding: 384-dimensional vector (all-MiniLM-L6-v2)
            metadata: Additional metadata (message_type, session_id, etc.)

        Returns:
            ID of saved message
        """
        # Placeholder - actual implementation would use ChromaDB
        return "1"

    async def vector_search(
        self,
        project_id: str,
        query_embedding: List[float],
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using ChromaDB (for local storage).

        Args:
            project_id: Project ID to search within
            query_embedding: Query vector (384d)
            limit: Maximum number of results
            filters: Optional metadata filters

        Returns:
            List of matching messages with similarity scores
        """
        # Placeholder - actual implementation would use ChromaDB
        return []

    # ==================
    # Summary Methods (SQLite)
    # ==================

    async def get_summary(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project summary from SQLite."""
        query = text("""
            SELECT summary, key_decisions, tech_stack, patterns, gotchas, last_updated, version, last_summarized_message_id
            FROM project_summaries WHERE project_id = :project_id
        """)
        result = await self._db.execute(query, {"project_id": project_id})
        row = result.fetchone()
        if row:
            return {
                "summary": row.summary,
                "key_decisions": row.key_decisions if row.key_decisions else "[]",
                "tech_stack": row.tech_stack if row.tech_stack else "[]",
                "patterns": row.patterns if row.patterns else "[]",
                "gotchas": row.gotchas if row.gotchas else "[]",
                "last_updated": row.last_updated,
                "version": row.version if hasattr(row, 'version') else 1,
                "last_summarized_message_id": row.last_summarized_message_id if hasattr(row, 'last_summarized_message_id') else None
            }
        return None

    async def update_summary(
        self,
        project_id: str,
        summary: str,
        trigger: Optional[str] = None,
        last_summarized_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update or create project summary in SQLite."""
        now = datetime.utcnow()

        # Check if exists
        existing = await self.get_summary(project_id)

        if existing:
            current_summary = existing.get("summary", "")
            if trigger:
                updated_summary = f"{current_summary}\n\n[{now.isoformat()}] {trigger}:\n{summary}"
            else:
                updated_summary = f"{current_summary}\n\n{summary}"

            # Truncate if too long
            if len(updated_summary) > 15000:
                updated_summary = updated_summary[-15000:]

            if last_summarized_message_id:
                query = text("""
                    UPDATE project_summaries
                    SET summary = :summary, last_updated = :last_updated, version = version + 1,
                        last_summarized_message_id = :last_message_id
                    WHERE project_id = :project_id
                """)
                await self._db.execute(query, {
                    "project_id": project_id,
                    "summary": updated_summary,
                    "last_updated": now,
                    "last_message_id": last_summarized_message_id
                })
            else:
                query = text("""
                    UPDATE project_summaries
                    SET summary = :summary, last_updated = :last_updated, version = version + 1
                    WHERE project_id = :project_id
                """)
                await self._db.execute(query, {
                    "project_id": project_id,
                    "summary": updated_summary,
                    "last_updated": now
                })
            await self._db.commit()
            return {"summary": updated_summary, "last_updated": now, "version": existing.get("version", 0) + 1}
        else:
            if last_summarized_message_id:
                query = text("""
                    INSERT INTO project_summaries
                    (project_id, summary, key_decisions, tech_stack, patterns, gotchas, last_updated, last_summarized_message_id)
                    VALUES (:project_id, :summary, '[]', '[]', '[]', '[]', :last_updated, :last_message_id)
                """)
                await self._db.execute(query, {
                    "project_id": project_id,
                    "summary": summary,
                    "last_updated": now,
                    "last_message_id": last_summarized_message_id
                })
            else:
                query = text("""
                    INSERT INTO project_summaries
                    (project_id, summary, key_decisions, tech_stack, patterns, gotchas, last_updated)
                    VALUES (:project_id, :summary, '[]', '[]', '[]', '[]', :last_updated)
                """)
                await self._db.execute(query, {
                    "project_id": project_id,
                    "summary": summary,
                    "last_updated": now
                })
            await self._db.commit()
            return {"summary": summary, "last_updated": now, "version": 1}

    async def get_stats(self, project_id: str) -> Dict[str, Any]:
        """Get memory statistics for a project from SQLite."""
        # Count messages
        count_query = text("SELECT COUNT(*) as count FROM conversation_memory WHERE project_id = :project_id")
        result = await self._db.execute(count_query, {"project_id": project_id})
        row = result.fetchone()
        message_count = row[0] if row else 0

        # Get summary info
        summary = await self.get_summary(project_id)

        return {
            "total_messages": message_count,
            "summary_last_updated": summary.get("last_updated") if summary else None,
            "summary_version": summary.get("version", 0) if summary else 0,
        }

    async def should_summarize(self, project_id: str, threshold: int = 30) -> Dict[str, Any]:
        """Check if project needs summarization in SQLite."""
        summary = await self.get_summary(project_id)
        last_summarized_id = summary.get("last_summarized_message_id") if summary else None

        if last_summarized_id:
            query = text("""
                SELECT COUNT(*) as count FROM conversation_memory
                WHERE project_id = :project_id AND id > :last_id
            """)
            result = await self._db.execute(query, {"project_id": project_id, "last_id": int(last_summarized_id)})
        else:
            query = text("SELECT COUNT(*) as count FROM conversation_memory WHERE project_id = :project_id")
            result = await self._db.execute(query, {"project_id": project_id})

        row = result.fetchone()
        messages_since = row[0] if row else 0

        return {
            "should_summarize": messages_since >= threshold,
            "messages_since_last_summary": messages_since,
            "threshold": threshold
        }

    async def get_sessions(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get unique sessions for a project from SQLite."""
        query = text("""
            SELECT session_id, MIN(timestamp) as first_message, MAX(timestamp) as last_message, COUNT(*) as message_count
            FROM conversation_memory
            WHERE project_id = :project_id AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY last_message DESC
            LIMIT :limit
        """)
        result = await self._db.execute(query, {"project_id": project_id, "limit": limit})
        rows = result.fetchall()
        return [
            {
                "session_id": row.session_id,
                "first_message": row.first_message,
                "last_message": row.last_message,
                "message_count": row.message_count
            }
            for row in rows
        ]

    async def get_session_messages(self, project_id: str, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a specific session from SQLite."""
        query = text("""
            SELECT * FROM conversation_memory
            WHERE project_id = :project_id AND session_id = :session_id
            ORDER BY timestamp ASC
            LIMIT :limit
        """)
        result = await self._db.execute(query, {"project_id": project_id, "session_id": session_id, "limit": limit})
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

    async def get_current_session(self, project_id: str) -> Optional[str]:
        """Get the most recent session ID from SQLite."""
        query = text("""
            SELECT session_id FROM conversation_memory
            WHERE project_id = :project_id AND session_id IS NOT NULL
            ORDER BY timestamp DESC LIMIT 1
        """)
        result = await self._db.execute(query, {"project_id": project_id})
        row = result.fetchone()
        return row.session_id if row else None


class MongoDBMemoryRepository(BaseRepository):
    """
    MongoDB implementation of conversation memory repository.

    Uses MongoDB Atlas Vector Search with voyage-3-large embeddings (1024d).
    Provides superior semantic search capabilities compared to ChromaDB.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB memory repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._collection = db["conversation_memory"]

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation message by ID from MongoDB."""
        from bson import ObjectId

        try:
            doc = await self._collection.find_one({"_id": ObjectId(id)})
            if doc:
                return self._doc_to_message(doc)
        except Exception:
            pass

        return None

    async def create(self, entity: Any) -> str:
        """Create new conversation message in MongoDB."""
        doc = self._message_to_doc(entity)
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update conversation message in MongoDB."""
        from bson import ObjectId

        doc = self._message_to_doc(entity)
        message_id = entity.get("id") if isinstance(entity, dict) else entity.id

        await self._collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete conversation message from MongoDB."""
        from bson import ObjectId

        await self._collection.delete_one({"_id": ObjectId(id)})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List conversation messages from MongoDB."""
        query = {}

        # Apply filters if provided
        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "session_id" in filters:
                query["session_id"] = filters["session_id"]
            if "task_id" in filters:
                query["task_id"] = filters["task_id"]
            if "message_type" in filters:
                query["message_type"] = filters["message_type"]

        cursor = (
            self._collection
            .find(query)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_message(doc) for doc in docs]

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count conversation messages in MongoDB."""
        query = {}

        # Apply filters if provided
        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]

        return await self._collection.count_documents(query)

    async def save_message(
        self,
        project_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save conversation message with voyage-3-large embedding.

        Args:
            project_id: Project ID
            content: Message content
            embedding: 1024-dimensional vector (voyage-3-large)
            metadata: Additional metadata (message_type, session_id, task_id, etc.)

        Returns:
            ID of saved message (ObjectId as string)
        """
        doc = {
            "project_id": project_id,
            "content": content,
            "embedding": embedding,  # 1024-dimensional vector
            "message_type": metadata.get("message_type", "assistant"),
            "session_id": metadata.get("session_id"),
            "task_id": metadata.get("task_id"),
            "timestamp": datetime.utcnow(),
            "metadata": metadata
        }

        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def vector_search(
        self,
        project_id: str,
        query_embedding: List[float],
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using MongoDB Atlas Vector Search.

        Uses cosine similarity for comparing voyage-3-large embeddings (1024d).

        Args:
            project_id: Project ID to search within
            query_embedding: Query vector (1024d from voyage-3-large)
            limit: Maximum number of results
            filters: Optional metadata filters (session_id, task_id, date_range)

        Returns:
            List of matching messages with similarity scores

        Note:
            Requires MongoDB Atlas Vector Search index 'vector_search_idx' on 'embedding' field.
            Index must be created via Atlas UI with:
            - Field: embedding
            - Dimensions: 1024
            - Similarity: cosine
        """
        # Build aggregation pipeline for vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_search_idx",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": min(limit * 5, 100),  # Fetch more candidates for better results
                    "limit": limit
                }
            },
            {
                "$match": {"project_id": project_id}
            }
        ]

        # Add metadata filters if provided
        if filters:
            match_filters = {"project_id": project_id}

            if "session_id" in filters:
                match_filters["session_id"] = filters["session_id"]
            if "task_id" in filters:
                match_filters["task_id"] = filters["task_id"]
            if "message_type" in filters:
                match_filters["message_type"] = filters["message_type"]
            if "start_date" in filters and "end_date" in filters:
                match_filters["timestamp"] = {
                    "$gte": filters["start_date"],
                    "$lte": filters["end_date"]
                }

            # Replace the match stage
            pipeline[1] = {"$match": match_filters}

        # Add projection to include similarity score
        pipeline.append({
            "$project": {
                "_id": 1,
                "project_id": 1,
                "content": 1,
                "message_type": 1,
                "session_id": 1,
                "task_id": 1,
                "timestamp": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        })

        # Execute aggregation
        cursor = self._collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)

        return [self._doc_to_message(doc) for doc in docs]

    async def create_vector_index(self):
        """
        Create MongoDB Atlas Vector Search index.

        Note: This is typically done via MongoDB Atlas UI, but can be automated
        via Atlas Admin API. For now, this is a placeholder.

        Required index configuration:
        {
          "name": "vector_search_idx",
          "type": "vectorSearch",
          "definition": {
            "fields": [{
              "type": "vector",
              "path": "embedding",
              "numDimensions": 1024,
              "similarity": "cosine"
            }]
          }
        }
        """
        # Placeholder - actual index creation done via Atlas UI or Admin API
        pass

    def _message_to_doc(self, message: Any) -> Dict[str, Any]:
        """
        Convert message to MongoDB document.

        Args:
            message: Message dict or object

        Returns:
            MongoDB document dictionary
        """
        if isinstance(message, dict):
            return message

        return {
            "project_id": message.project_id,
            "content": message.content,
            "embedding": message.embedding,
            "message_type": message.message_type,
            "session_id": message.session_id,
            "task_id": message.task_id,
            "timestamp": message.timestamp or datetime.utcnow(),
            "metadata": message.metadata or {}
        }

    def _doc_to_message(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document to message dict.

        Args:
            doc: MongoDB document

        Returns:
            Message dictionary
        """
        return {
            "id": str(doc["_id"]),
            "project_id": doc["project_id"],
            "content": doc["content"],
            "embedding": doc.get("embedding"),
            "message_type": doc.get("message_type", "assistant"),
            "session_id": doc.get("session_id"),
            "task_id": doc.get("task_id"),
            "timestamp": doc.get("timestamp"),
            "metadata": doc.get("metadata", {}),
            "score": doc.get("score")  # Similarity score from vector search
        }

    # ==================
    # Summary Methods
    # ==================

    async def get_summary(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project summary from MongoDB.

        Args:
            project_id: Project ID

        Returns:
            Summary document or None if not exists
        """
        summaries = self._db["project_summaries"]
        doc = await summaries.find_one({"project_id": project_id})
        if doc:
            return {
                "summary": doc.get("summary", ""),
                "key_decisions": doc.get("key_decisions", []),
                "tech_stack": doc.get("tech_stack", []),
                "patterns": doc.get("patterns", []),
                "gotchas": doc.get("gotchas", []),
                "last_updated": doc.get("last_updated"),
                "version": doc.get("version", 1),
                "last_summarized_message_id": doc.get("last_summarized_message_id")
            }
        return None

    async def update_summary(
        self,
        project_id: str,
        summary: str,
        trigger: Optional[str] = None,
        last_summarized_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update or create project summary in MongoDB.

        Args:
            project_id: Project ID
            summary: New summary content
            trigger: Trigger type (session_end, important_decision, task_complete)
            last_summarized_message_id: ID of last message included in summary

        Returns:
            Updated summary document
        """
        summaries = self._db["project_summaries"]
        now = datetime.utcnow()

        # Check if summary exists
        existing = await summaries.find_one({"project_id": project_id})

        if existing:
            # Append to existing summary
            current_summary = existing.get("summary", "")
            if trigger:
                updated_summary = f"{current_summary}\n\n[{now.isoformat()}] {trigger}:\n{summary}"
            else:
                updated_summary = f"{current_summary}\n\n{summary}"

            # Truncate if too long (keep last 15000 chars)
            if len(updated_summary) > 15000:
                updated_summary = updated_summary[-15000:]

            update_data = {
                "$set": {
                    "summary": updated_summary,
                    "last_updated": now,
                },
                "$inc": {"version": 1}
            }

            if last_summarized_message_id:
                update_data["$set"]["last_summarized_message_id"] = last_summarized_message_id

            await summaries.update_one(
                {"project_id": project_id},
                update_data
            )

            return {
                "summary": updated_summary,
                "last_updated": now,
                "version": existing.get("version", 0) + 1
            }
        else:
            # Create new summary
            doc = {
                "project_id": project_id,
                "summary": summary,
                "key_decisions": [],
                "tech_stack": [],
                "patterns": [],
                "gotchas": [],
                "last_updated": now,
                "version": 1,
                "last_summarized_message_id": last_summarized_message_id
            }
            await summaries.insert_one(doc)
            return {
                "summary": summary,
                "last_updated": now,
                "version": 1
            }

    async def get_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a project.

        Args:
            project_id: Project ID

        Returns:
            Statistics dictionary
        """
        # Count messages
        message_count = await self._collection.count_documents({"project_id": project_id})

        # Get summary info
        summaries = self._db["project_summaries"]
        summary_doc = await summaries.find_one({"project_id": project_id})

        return {
            "total_messages": message_count,
            "summary_last_updated": summary_doc.get("last_updated") if summary_doc else None,
            "summary_version": summary_doc.get("version", 0) if summary_doc else 0,
        }

    async def should_summarize(
        self,
        project_id: str,
        threshold: int = 30
    ) -> Dict[str, Any]:
        """
        Check if project needs summarization.

        Args:
            project_id: Project ID
            threshold: Number of messages since last summary to trigger

        Returns:
            Dict with should_summarize flag and message count
        """
        # Get last summarized message ID
        summaries = self._db["project_summaries"]
        summary_doc = await summaries.find_one({"project_id": project_id})
        last_summarized_id = summary_doc.get("last_summarized_message_id") if summary_doc else None

        # Count messages since last summary
        if last_summarized_id:
            from bson import ObjectId
            try:
                messages_since = await self._collection.count_documents({
                    "project_id": project_id,
                    "_id": {"$gt": ObjectId(last_summarized_id)}
                })
            except Exception:
                messages_since = await self._collection.count_documents({"project_id": project_id})
        else:
            messages_since = await self._collection.count_documents({"project_id": project_id})

        return {
            "should_summarize": messages_since >= threshold,
            "messages_since_last_summary": messages_since,
            "threshold": threshold
        }

    async def get_sessions(
        self,
        project_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get unique sessions for a project.

        Args:
            project_id: Project ID
            limit: Maximum number of sessions

        Returns:
            List of session info dicts
        """
        pipeline = [
            {"$match": {"project_id": project_id, "session_id": {"$ne": None}}},
            {"$group": {
                "_id": "$session_id",
                "first_message": {"$min": "$timestamp"},
                "last_message": {"$max": "$timestamp"},
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"last_message": -1}},
            {"$limit": limit}
        ]

        cursor = self._collection.aggregate(pipeline)
        sessions = await cursor.to_list(length=limit)

        return [
            {
                "session_id": s["_id"],
                "first_message": s["first_message"],
                "last_message": s["last_message"],
                "message_count": s["message_count"]
            }
            for s in sessions
        ]

    async def get_session_messages(
        self,
        project_id: str,
        session_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a specific session.

        Args:
            project_id: Project ID
            session_id: Session ID
            limit: Maximum number of messages

        Returns:
            List of messages
        """
        cursor = (
            self._collection
            .find({"project_id": project_id, "session_id": session_id})
            .sort("timestamp", 1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_message(doc) for doc in docs]

    async def get_current_session(self, project_id: str) -> Optional[str]:
        """
        Get the most recent session ID for a project.

        Args:
            project_id: Project ID

        Returns:
            Session ID or None
        """
        doc = await self._collection.find_one(
            {"project_id": project_id, "session_id": {"$ne": None}},
            sort=[("timestamp", -1)]
        )
        return doc.get("session_id") if doc else None
