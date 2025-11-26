"""API endpoints for cloud storage configuration (MongoDB Atlas + Voyage AI)"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings/cloud-storage", tags=["cloud-storage"])


class CloudStorageConfig(BaseModel):
    """
    Cloud storage configuration model.

    Includes MongoDB Atlas connection credentials and Voyage AI API key.
    """
    connection_string: str = Field(
        ...,
        description="MongoDB connection string (mongodb+srv://...)",
        min_length=1
    )
    database_name: str = Field(
        default="claudetask",
        description="MongoDB database name"
    )
    voyage_api_key: str = Field(
        ...,
        description="Voyage AI API key for voyage-3-large embeddings",
        min_length=1
    )


class CloudStorageStatus(BaseModel):
    """Cloud storage configuration status."""
    configured: bool = Field(description="Whether MongoDB Atlas is configured")
    connection_string_set: bool = Field(description="Whether connection string is set")
    voyage_api_key_set: bool = Field(description="Whether Voyage AI API key is set")


class ConnectionTestResult(BaseModel):
    """Result of testing MongoDB and Voyage AI connections."""
    mongodb_connected: bool = Field(default=False, description="MongoDB connection successful")
    voyage_ai_valid: bool = Field(default=False, description="Voyage AI API key valid")
    database_writable: bool = Field(default=False, description="Database has write permissions")
    error: Optional[str] = Field(default=None, description="Error message if connection failed")


@router.get("/status", response_model=CloudStorageStatus)
async def get_cloud_storage_status():
    """
    Check if MongoDB Atlas and Voyage AI are configured.

    Returns:
        Configuration status with boolean flags

    Example:
        GET /api/settings/cloud-storage/status
        {
          "configured": true,
          "connection_string_set": true,
          "voyage_api_key_set": true
        }
    """
    connection_string_set = bool(os.getenv("MONGODB_CONNECTION_STRING"))
    voyage_api_key_set = bool(os.getenv("VOYAGE_AI_API_KEY"))

    return CloudStorageStatus(
        configured=connection_string_set and voyage_api_key_set,
        connection_string_set=connection_string_set,
        voyage_api_key_set=voyage_api_key_set
    )


@router.post("/test", response_model=ConnectionTestResult)
async def test_cloud_storage_connection(config: CloudStorageConfig):
    """
    Test MongoDB Atlas and Voyage AI connections before saving.

    This endpoint validates:
    1. MongoDB connection string format and connectivity
    2. Database write permissions
    3. Voyage AI API key validity

    Args:
        config: Cloud storage configuration to test

    Returns:
        Test results for MongoDB and Voyage AI

    Example:
        POST /api/settings/cloud-storage/test
        {
          "connection_string": "mongodb+srv://...",
          "database_name": "claudetask",
          "voyage_api_key": "vo-..."
        }

        Response:
        {
          "mongodb_connected": true,
          "voyage_ai_valid": true,
          "database_writable": true,
          "error": null
        }
    """
    results = ConnectionTestResult()

    # Test MongoDB connection
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        # Create temporary client with test configuration
        client = AsyncIOMotorClient(
            config.connection_string,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=False
        )

        # Ping database to verify connection
        await client.admin.command('ping')
        results.mongodb_connected = True

        # Test write permissions
        db = client[config.database_name]
        test_collection = db["_connection_test"]
        await test_collection.insert_one({"test": "connection"})
        await test_collection.delete_one({"test": "connection"})
        results.database_writable = True

        # Close test client
        client.close()

    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        results.error = f"MongoDB error: {str(e)}"
        return results

    # Test Voyage AI API
    try:
        import voyageai

        # Create Voyage AI client
        client = voyageai.Client(api_key=config.voyage_api_key)

        # Test embedding generation with a simple text
        client.embed(["test"], model="voyage-3-large")
        results.voyage_ai_valid = True

    except Exception as e:
        logger.error(f"Voyage AI API test failed: {e}")
        results.error = f"Voyage AI error: {str(e)}"
        return results

    return results


@router.post("/save")
async def save_cloud_storage_config(config: CloudStorageConfig):
    """
    Save MongoDB Atlas and Voyage AI configuration to .env file.

    This endpoint:
    1. Updates or adds MongoDB and Voyage AI credentials to .env file
    2. Updates current process environment variables
    3. Requires application restart for full effect

    Args:
        config: Cloud storage configuration to save

    Returns:
        Save status and restart requirement

    Raises:
        HTTPException: If unable to write to .env file

    Example:
        POST /api/settings/cloud-storage/save
        {
          "connection_string": "mongodb+srv://...",
          "database_name": "claudetask",
          "voyage_api_key": "vo-..."
        }

        Response:
        {
          "status": "saved",
          "restart_required": true,
          "message": "Configuration saved successfully. Restart application to apply changes."
        }
    """
    try:
        # Get .env file path (relative to backend directory)
        env_path = Path(__file__).parent.parent.parent.parent / ".env"

        # Read existing .env file
        env_lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_lines = f.readlines()

        # Configuration keys to update
        keys_to_update = {
            "MONGODB_CONNECTION_STRING": config.connection_string,
            "MONGODB_DATABASE_NAME": config.database_name,
            "VOYAGE_AI_API_KEY": config.voyage_api_key
        }

        # Update existing lines or mark for addition
        updated_lines = []
        keys_updated = set()

        for line in env_lines:
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                updated_lines.append(line)
                continue

            # Extract key from line
            if '=' in line:
                key = line.split('=')[0].strip()

                # Update if key matches
                if key in keys_to_update:
                    updated_lines.append(f"{key}={keys_to_update[key]}\n")
                    keys_updated.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add missing keys at the end
        if keys_updated != set(keys_to_update.keys()):
            # Add section header if adding new keys
            if not keys_updated:
                updated_lines.append("\n# MongoDB Atlas Configuration\n")

            for key, value in keys_to_update.items():
                if key not in keys_updated:
                    updated_lines.append(f"{key}={value}\n")

        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)

        # Update current environment (for immediate use without restart)
        os.environ.update(keys_to_update)

        logger.info("Cloud storage configuration saved successfully")

        return {
            "status": "saved",
            "restart_required": True,
            "message": "Configuration saved successfully. Restart application to apply changes."
        }

    except Exception as e:
        logger.error(f"Failed to save cloud storage configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.delete("/config")
async def delete_cloud_storage_config():
    """
    Remove MongoDB Atlas and Voyage AI configuration from .env file.

    This endpoint:
    1. Removes MongoDB and Voyage AI credentials from .env file
    2. Updates current process environment variables
    3. Disconnects MongoDB if connected

    Returns:
        Deletion status

    Example:
        DELETE /api/settings/cloud-storage/config

        Response:
        {
          "status": "deleted",
          "message": "Cloud storage configuration removed successfully."
        }
    """
    try:
        # Get .env file path
        env_path = Path(__file__).parent.parent.parent.parent / ".env"

        if not env_path.exists():
            return {
                "status": "not_found",
                "message": "No .env file found"
            }

        # Read existing .env file
        with open(env_path, 'r') as f:
            env_lines = f.readlines()

        # Keys to remove
        keys_to_remove = {
            "MONGODB_CONNECTION_STRING",
            "MONGODB_DATABASE_NAME",
            "VOYAGE_AI_API_KEY"
        }

        # Filter out lines with these keys
        updated_lines = []
        for line in env_lines:
            if '=' in line:
                key = line.split('=')[0].strip()
                if key not in keys_to_remove:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)

        # Remove from current environment
        for key in keys_to_remove:
            os.environ.pop(key, None)

        # Disconnect MongoDB if connected
        try:
            from ..database_mongodb import mongodb_manager
            await mongodb_manager.disconnect()
        except Exception:
            pass

        logger.info("Cloud storage configuration removed successfully")

        return {
            "status": "deleted",
            "message": "Cloud storage configuration removed successfully."
        }

    except Exception as e:
        logger.error(f"Failed to delete cloud storage configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete configuration: {str(e)}"
        )


@router.get("/health")
async def cloud_storage_health():
    """
    Check MongoDB Atlas connection health.

    Returns:
        Health status including connectivity and write permissions

    Example:
        GET /api/settings/cloud-storage/health

        Response:
        {
          "connected": true,
          "database": "claudetask",
          "writable": true,
          "error": null
        }
    """
    try:
        from ..database_mongodb import mongodb_manager

        health_status = await mongodb_manager.health_check()
        return health_status

    except Exception as e:
        logger.error(f"Cloud storage health check failed: {e}")
        return {
            "connected": False,
            "database": "claudetask",
            "writable": False,
            "error": str(e)
        }
