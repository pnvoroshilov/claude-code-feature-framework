"""MongoDB Atlas connection manager using Motor async driver"""

import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class MongoDBManager:
    """
    MongoDB Atlas connection manager with connection pooling and TLS support.

    This manager handles:
    - Connection lifecycle (connect, disconnect)
    - Connection pooling (configurable pool size)
    - TLS/SSL enforcement for security
    - Automatic reconnection with retries
    - Health checks and connection validation

    Usage:
        mongodb_manager = MongoDBManager()
        await mongodb_manager.connect()
        db = mongodb_manager.get_database()
        # Use db for operations
        await mongodb_manager.disconnect()
    """

    def __init__(self):
        """
        Initialize MongoDB manager.

        Configuration is read from environment variables:
        - MONGODB_CONNECTION_STRING: MongoDB connection string (required)
        - MONGODB_DATABASE_NAME: Database name (default: "claudetask")
        """
        self.client: Optional[AsyncIOMotorClient] = None
        self.db_name: str = os.getenv("MONGODB_DATABASE_NAME", "claudetask")

    async def connect(self):
        """
        Connect to MongoDB Atlas with TLS and connection pooling.

        Connection configuration:
        - maxPoolSize=10: Maximum 10 concurrent connections
        - minPoolSize=1: Keep 1 connection open for fast queries
        - maxIdleTimeMS=30000: Close idle connections after 30s
        - serverSelectionTimeoutMS=5000: Timeout after 5s if server unreachable
        - tls=True: Enforce TLS/SSL encryption
        - tlsAllowInvalidCertificates=False: Reject invalid certificates

        Raises:
            ValueError: If MONGODB_CONNECTION_STRING not set
            ConnectionError: If unable to connect to MongoDB
        """
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")

        if not connection_string:
            raise ValueError(
                "MONGODB_CONNECTION_STRING not set in environment. "
                "Configure MongoDB Atlas credentials via Settings → Cloud Storage."
            )

        try:
            self.client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=10,  # Maximum concurrent connections
                minPoolSize=1,  # Minimum connections to keep open
                maxIdleTimeMS=30000,  # Close idle connections after 30s
                serverSelectionTimeoutMS=5000,  # Timeout after 5s
                tls=True,  # Enforce TLS encryption
                tlsAllowInvalidCertificates=False  # Reject invalid certificates
            )

            # Test connection with ping
            await self.client.admin.command('ping')

            logger.info(f"Connected to MongoDB Atlas: database='{self.db_name}'")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise ConnectionError(f"MongoDB connection failed: {e}")

    async def disconnect(self):
        """
        Close MongoDB connection and release resources.

        This should be called during application shutdown to ensure
        graceful cleanup of connection pool.
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
            self.client = None

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get MongoDB database instance.

        Returns:
            Motor async database instance

        Raises:
            RuntimeError: If MongoDB not connected (call connect() first)
        """
        if not self.client:
            raise RuntimeError(
                "MongoDB not connected. Call connect() first or check "
                "MongoDB Atlas configuration in Settings → Cloud Storage."
            )

        return self.client[self.db_name]

    async def health_check(self) -> dict:
        """
        Perform health check on MongoDB connection.

        Returns:
            Health status dictionary with:
            - connected: bool
            - database: str
            - writable: bool
            - error: Optional[str]

        Usage:
            GET /api/health/mongodb endpoint
        """
        status = {
            "connected": False,
            "database": self.db_name,
            "writable": False,
            "error": None
        }

        if not self.client:
            status["error"] = "MongoDB not connected"
            return status

        try:
            # Check connection
            await self.client.admin.command('ping')
            status["connected"] = True

            # Check write permissions
            db = self.get_database()
            test_collection = db["_health_check"]
            await test_collection.insert_one({"test": "health_check"})
            await test_collection.delete_one({"test": "health_check"})
            status["writable"] = True

        except Exception as e:
            status["error"] = str(e)

        return status

    async def create_indexes(self):
        """
        Create MongoDB indexes for optimal query performance.

        Indexes:
        - conversation_memory: project_id, session_id, task_id, timestamp
        - tasks: project_id, status, created_at
        - projects: path (unique), is_active
        - Vector Search index for RAG (created automatically)
        """
        if not self.client:
            raise RuntimeError("MongoDB not connected")

        db = self.get_database()

        # Conversation memory indexes
        await db.conversation_memory.create_index("project_id")
        await db.conversation_memory.create_index("session_id")
        await db.conversation_memory.create_index("task_id")
        await db.conversation_memory.create_index([("timestamp", -1)])

        # Task indexes
        await db.tasks.create_index("project_id")
        await db.tasks.create_index("status")
        await db.tasks.create_index([("created_at", -1)])

        # Project indexes
        await db.projects.create_index("path", unique=True)
        await db.projects.create_index("is_active")

        logger.info("MongoDB indexes created successfully")

        # Create Vector Search index for RAG
        await self.create_vector_search_index()

        # Create skill indexes
        await self.create_skill_indexes()

    async def create_skill_indexes(self):
        """
        Create MongoDB indexes for skills collections.

        Collections:
        - default_skills: Global framework skills
        - custom_skills: User-created skills per project
        - project_skills: Junction table for enabled skills
        """
        if not self.client:
            raise RuntimeError("MongoDB not connected")

        db = self.get_database()

        # Default skills indexes
        await db.default_skills.create_index("name", unique=True)
        await db.default_skills.create_index("is_active")
        await db.default_skills.create_index("is_favorite")
        await db.default_skills.create_index("category")

        # Custom skills indexes
        await db.custom_skills.create_index("project_id")
        await db.custom_skills.create_index([("project_id", 1), ("name", 1)], unique=True)
        await db.custom_skills.create_index("is_favorite")
        await db.custom_skills.create_index("status")

        # Project skills (junction) indexes
        await db.project_skills.create_index("project_id")
        await db.project_skills.create_index([
            ("project_id", 1),
            ("skill_id", 1),
            ("skill_type", 1)
        ], unique=True)

        logger.info("Skill indexes created successfully")

        # Create hook indexes
        await self.create_hook_indexes()

    async def create_hook_indexes(self):
        """
        Create MongoDB indexes for hooks collections.

        Collections:
        - default_hooks: Global framework hooks
        - custom_hooks: User-created hooks per project
        - project_hooks: Junction table for enabled hooks
        """
        if not self.client:
            raise RuntimeError("MongoDB not connected")

        db = self.get_database()

        # Default hooks indexes
        await db.default_hooks.create_index("name", unique=True)
        await db.default_hooks.create_index("is_active")
        await db.default_hooks.create_index("is_favorite")
        await db.default_hooks.create_index("category")

        # Custom hooks indexes
        await db.custom_hooks.create_index("project_id")
        await db.custom_hooks.create_index([("project_id", 1), ("name", 1)], unique=True)
        await db.custom_hooks.create_index("is_favorite")
        await db.custom_hooks.create_index("status")

        # Project hooks (junction) indexes
        await db.project_hooks.create_index("project_id")
        await db.project_hooks.create_index([
            ("project_id", 1),
            ("hook_id", 1),
            ("hook_type", 1)
        ], unique=True)

        logger.info("Hook indexes created successfully")

        # Create MCP config indexes
        await self.create_mcp_config_indexes()

    async def create_mcp_config_indexes(self):
        """
        Create MongoDB indexes for MCP config collections.

        Collections:
        - default_mcp_configs: Global framework MCP configs
        - custom_mcp_configs: User-created MCP configs per project
        - project_mcp_configs: Junction table for enabled configs
        """
        if not self.client:
            raise RuntimeError("MongoDB not connected")

        db = self.get_database()

        # Default MCP configs indexes
        await db.default_mcp_configs.create_index("name", unique=True)
        await db.default_mcp_configs.create_index("is_active")
        await db.default_mcp_configs.create_index("is_favorite")
        await db.default_mcp_configs.create_index("category")

        # Custom MCP configs indexes
        await db.custom_mcp_configs.create_index("project_id")
        await db.custom_mcp_configs.create_index([("project_id", 1), ("name", 1)], unique=True)
        await db.custom_mcp_configs.create_index("is_favorite")
        await db.custom_mcp_configs.create_index("status")
        await db.custom_mcp_configs.create_index("category")

        # Project MCP configs (junction) indexes
        await db.project_mcp_configs.create_index("project_id")
        await db.project_mcp_configs.create_index([
            ("project_id", 1),
            ("mcp_config_id", 1),
            ("mcp_config_type", 1)
        ], unique=True)

        logger.info("MCP config indexes created successfully")

        # Create subagent indexes
        await self.create_subagent_indexes()

    async def create_subagent_indexes(self):
        """
        Create MongoDB indexes for subagents collections.

        Collections:
        - default_subagents: Global framework subagents
        - custom_subagents: User-created subagents per project
        - project_subagents: Junction table for enabled subagents
        - subagent_skills: Junction table for skill assignments
        """
        if not self.client:
            raise RuntimeError("MongoDB not connected")

        db = self.get_database()

        # Default subagents indexes
        await db.default_subagents.create_index("name", unique=True)
        await db.default_subagents.create_index("is_active")
        await db.default_subagents.create_index("is_favorite")
        await db.default_subagents.create_index("category")

        # Custom subagents indexes
        await db.custom_subagents.create_index("project_id")
        await db.custom_subagents.create_index([("project_id", 1), ("name", 1)], unique=True)
        await db.custom_subagents.create_index("is_favorite")
        await db.custom_subagents.create_index("status")

        # Project subagents (junction) indexes
        await db.project_subagents.create_index("project_id")
        await db.project_subagents.create_index([
            ("project_id", 1),
            ("subagent_id", 1),
            ("subagent_type", 1)
        ], unique=True)

        # Subagent skills (junction) indexes
        await db.subagent_skills.create_index("subagent_id")
        await db.subagent_skills.create_index([
            ("subagent_id", 1),
            ("subagent_type", 1),
            ("skill_id", 1),
            ("skill_type", 1)
        ], unique=True)

        logger.info("Subagent indexes created successfully")

    async def create_vector_search_indexes(self):
        """
        Create all MongoDB Atlas Vector Search indexes for RAG.

        Creates indexes for:
        1. codebase_chunks - Codebase semantic search
        2. project_summaries - Project summary semantic search
        3. documentation_chunks - Documentation semantic search
        """
        if not self.client:
            raise RuntimeError("MongoDB not connected")

        try:
            from pymongo import MongoClient
            from pymongo.operations import SearchIndexModel

            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            sync_client = MongoClient(connection_string)
            sync_db = sync_client[self.db_name]

            # Define all vector search indexes
            indexes_config = [
                {
                    "collection": "codebase_chunks",
                    "index_name": "codebase_vector_idx",
                    "fields": [
                        {"type": "vector", "path": "embedding", "numDimensions": 1024, "similarity": "cosine"},
                        {"type": "filter", "path": "project_id"},
                        {"type": "filter", "path": "language"},
                        {"type": "filter", "path": "chunk_type"}
                    ]
                },
                {
                    "collection": "project_summaries",
                    "index_name": "summary_vector_idx",
                    "fields": [
                        {"type": "vector", "path": "embedding", "numDimensions": 1024, "similarity": "cosine"},
                        {"type": "filter", "path": "project_id"}
                    ]
                },
                {
                    "collection": "documentation_chunks",
                    "index_name": "documentation_vector_idx",
                    "fields": [
                        {"type": "vector", "path": "embedding", "numDimensions": 1024, "similarity": "cosine"},
                        {"type": "filter", "path": "project_id"},
                        {"type": "filter", "path": "doc_type"}
                    ]
                }
            ]

            for config in indexes_config:
                collection = sync_db[config["collection"]]

                # Check if index already exists
                try:
                    existing_indexes = list(collection.list_search_indexes())
                    index_names = [idx.get("name") for idx in existing_indexes]

                    if config["index_name"] in index_names:
                        logger.info(f"Vector Search index '{config['index_name']}' already exists on {config['collection']}")
                        continue
                except Exception:
                    # Collection might not exist yet - that's fine
                    pass

                # Create Vector Search index
                search_index_model = SearchIndexModel(
                    definition={"fields": config["fields"]},
                    name=config["index_name"],
                    type="vectorSearch"
                )

                try:
                    result = collection.create_search_index(model=search_index_model)
                    logger.info(f"Vector Search index '{config['index_name']}' created on {config['collection']}: {result}")
                except Exception as e:
                    logger.warning(f"Could not create index '{config['index_name']}' on {config['collection']}: {e}")

            sync_client.close()
            logger.info("All Vector Search indexes initialized")

        except Exception as e:
            logger.warning(f"Could not create Vector Search indexes: {e}")

    # Backward compatibility alias
    async def create_vector_search_index(self):
        """Backward compatibility - calls create_vector_search_indexes"""
        await self.create_vector_search_indexes()


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Dependency for FastAPI endpoints to get MongoDB database.

    Usage:
        @app.get("/api/example")
        async def example(db: AsyncIOMotorDatabase = Depends(get_mongodb)):
            collection = db["my_collection"]
            # Use collection

    Returns:
        Motor async database instance

    Raises:
        RuntimeError: If MongoDB not connected
    """
    return mongodb_manager.get_database()
