"""
Migration script: Migrate MCP Configs from SQLite to MongoDB

This script migrates:
- default_mcp_configs table → default_mcp_configs collection
- custom_mcp_configs table → custom_mcp_configs collection
- project_mcp_configs table → project_mcp_configs collection

Usage:
    cd claudetask/backend
    python -m migrations.migrate_mcp_configs_to_mongodb
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient


# Configuration
SQLITE_DB_PATH = os.getenv(
    "DATABASE_URL",
    "sqlite:///./claudetask.db"
).replace("sqlite:///", "")

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "claudetask")


async def migrate_mcp_configs():
    """Main migration function."""
    print("=" * 60)
    print("MCP Configs Migration: SQLite → MongoDB")
    print("=" * 60)

    if not MONGODB_CONNECTION_STRING:
        print("ERROR: MONGODB_CONNECTION_STRING not set")
        print("Please set the environment variable and try again")
        return

    # Connect to SQLite
    print(f"\n1. Connecting to SQLite: {SQLITE_DB_PATH}")
    engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
    Session = sessionmaker(bind=engine)
    sqlite_session = Session()

    # Connect to MongoDB
    print(f"2. Connecting to MongoDB: {MONGODB_DATABASE_NAME}")
    mongo_client = AsyncIOMotorClient(
        MONGODB_CONNECTION_STRING,
        tls=True,
        tlsAllowInvalidCertificates=False
    )
    mongodb = mongo_client[MONGODB_DATABASE_NAME]

    try:
        # Test MongoDB connection
        await mongo_client.admin.command('ping')
        print("   ✓ MongoDB connected")

        # Migrate default_mcp_configs
        print("\n3. Migrating default_mcp_configs...")
        await migrate_default_mcp_configs(sqlite_session, mongodb)

        # Migrate custom_mcp_configs
        print("\n4. Migrating custom_mcp_configs...")
        await migrate_custom_mcp_configs(sqlite_session, mongodb)

        # Migrate project_mcp_configs
        print("\n5. Migrating project_mcp_configs...")
        await migrate_project_mcp_configs(sqlite_session, mongodb)

        # Create indexes
        print("\n6. Creating indexes...")
        await create_indexes(mongodb)

        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

    finally:
        sqlite_session.close()
        mongo_client.close()


async def migrate_default_mcp_configs(sqlite_session, mongodb):
    """Migrate default_mcp_configs table."""
    # Check if already migrated
    existing_count = await mongodb.default_mcp_configs.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ default_mcp_configs already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_mcp_configs migration")
            return
        await mongodb.default_mcp_configs.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM default_mcp_configs"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No default_mcp_configs to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))

        # Parse config JSON if stored as string
        config = row_dict.get("config")
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}

        doc = {
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "General"),
            "config": config or {},
            "setup_instructions": row_dict.get("setup_instructions"),
            "dependencies": row_dict.get("dependencies"),
            "is_active": bool(row_dict.get("is_active", True)),
            "is_favorite": bool(row_dict.get("is_favorite", False)),
            "created_at": row_dict.get("created_at") or datetime.utcnow(),
            "updated_at": row_dict.get("updated_at") or datetime.utcnow(),
            "_sqlite_id": row_dict["id"]  # Keep reference to original ID
        }
        documents.append(doc)

    # Insert to MongoDB
    result = await mongodb.default_mcp_configs.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} default_mcp_configs")


async def migrate_custom_mcp_configs(sqlite_session, mongodb):
    """Migrate custom_mcp_configs table."""
    # Check if already migrated
    existing_count = await mongodb.custom_mcp_configs.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ custom_mcp_configs already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping custom_mcp_configs migration")
            return
        await mongodb.custom_mcp_configs.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM custom_mcp_configs"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No custom_mcp_configs to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))

        # Parse config JSON if stored as string
        config = row_dict.get("config")
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except:
                config = {}

        doc = {
            "project_id": row_dict["project_id"],
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "Custom"),
            "config": config or {},
            "setup_instructions": row_dict.get("setup_instructions"),
            "dependencies": row_dict.get("dependencies"),
            "status": row_dict.get("status", "active"),
            "error_message": row_dict.get("error_message"),
            "created_by": row_dict.get("created_by", "user"),
            "is_favorite": bool(row_dict.get("is_favorite", False)),
            "created_at": row_dict.get("created_at") or datetime.utcnow(),
            "updated_at": row_dict.get("updated_at") or datetime.utcnow(),
            "_sqlite_id": row_dict["id"]  # Keep reference to original ID
        }
        documents.append(doc)

    # Insert to MongoDB
    result = await mongodb.custom_mcp_configs.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} custom_mcp_configs")


async def migrate_project_mcp_configs(sqlite_session, mongodb):
    """Migrate project_mcp_configs junction table."""
    # Check if already migrated
    existing_count = await mongodb.project_mcp_configs.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ project_mcp_configs already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping project_mcp_configs migration")
            return
        await mongodb.project_mcp_configs.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM project_mcp_configs"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No project_mcp_configs to migrate")
        return

    # Build ID mapping from SQLite ID to MongoDB ObjectId
    default_id_map = await build_id_map(mongodb.default_mcp_configs)
    custom_id_map = await build_id_map(mongodb.custom_mcp_configs)

    # Convert to MongoDB documents
    documents = []
    skipped = 0
    for row in rows:
        row_dict = dict(zip(columns, row))
        config_type = row_dict["mcp_config_type"]
        sqlite_config_id = row_dict["mcp_config_id"]

        # Map SQLite ID to MongoDB ObjectId
        if config_type == "default":
            mongo_config_id = default_id_map.get(sqlite_config_id)
        else:
            mongo_config_id = custom_id_map.get(sqlite_config_id)

        if not mongo_config_id:
            print(f"   ⚠ Skipping: mcp_config_id={sqlite_config_id} ({config_type}) not found in MongoDB")
            skipped += 1
            continue

        doc = {
            "project_id": row_dict["project_id"],
            "mcp_config_id": str(mongo_config_id),  # Store as string for consistency
            "mcp_config_type": config_type,
            "enabled_at": row_dict.get("enabled_at") or datetime.utcnow(),
            "enabled_by": row_dict.get("enabled_by", "user")
        }
        documents.append(doc)

    # Insert to MongoDB
    if documents:
        result = await mongodb.project_mcp_configs.insert_many(documents)
        print(f"   ✓ Migrated {len(result.inserted_ids)} project_mcp_configs")
    if skipped:
        print(f"   ⚠ Skipped {skipped} records (config not found)")


async def build_id_map(collection):
    """Build mapping from SQLite ID to MongoDB ObjectId."""
    id_map = {}
    cursor = collection.find({}, {"_id": 1, "_sqlite_id": 1})
    async for doc in cursor:
        if "_sqlite_id" in doc:
            id_map[doc["_sqlite_id"]] = doc["_id"]
    return id_map


async def create_indexes(mongodb):
    """Create MongoDB indexes for MCP config collections."""
    # Default MCP configs indexes
    await mongodb.default_mcp_configs.create_index("name", unique=True)
    await mongodb.default_mcp_configs.create_index("is_active")
    await mongodb.default_mcp_configs.create_index("is_favorite")
    await mongodb.default_mcp_configs.create_index("category")
    print("   ✓ default_mcp_configs indexes created")

    # Custom MCP configs indexes
    await mongodb.custom_mcp_configs.create_index("project_id")
    await mongodb.custom_mcp_configs.create_index([("project_id", 1), ("name", 1)], unique=True)
    await mongodb.custom_mcp_configs.create_index("is_favorite")
    await mongodb.custom_mcp_configs.create_index("status")
    await mongodb.custom_mcp_configs.create_index("category")
    print("   ✓ custom_mcp_configs indexes created")

    # Project MCP configs indexes
    await mongodb.project_mcp_configs.create_index("project_id")
    await mongodb.project_mcp_configs.create_index([
        ("project_id", 1),
        ("mcp_config_id", 1),
        ("mcp_config_type", 1)
    ], unique=True)
    print("   ✓ project_mcp_configs indexes created")


if __name__ == "__main__":
    asyncio.run(migrate_mcp_configs())
