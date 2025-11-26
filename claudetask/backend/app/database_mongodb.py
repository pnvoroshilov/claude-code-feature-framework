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

        Note: Vector Search index must be created via MongoDB Atlas UI:
        - Collection: conversation_memory
        - Field: embedding
        - Dimensions: 1024
        - Similarity: cosine
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
