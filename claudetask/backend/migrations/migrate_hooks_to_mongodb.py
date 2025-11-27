"""
Migration script: Migrate Hooks from SQLite to MongoDB

This script migrates:
- default_hooks table → default_hooks collection
- custom_hooks table → custom_hooks collection
- project_hooks table → project_hooks collection

Usage:
    cd claudetask/backend
    python -m migrations.migrate_hooks_to_mongodb
"""

import asyncio
import os
import sys
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


async def migrate_hooks():
    """Main migration function."""
    print("=" * 60)
    print("Hooks Migration: SQLite → MongoDB")
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

        # Migrate default_hooks
        print("\n3. Migrating default_hooks...")
        await migrate_default_hooks(sqlite_session, mongodb)

        # Migrate custom_hooks
        print("\n4. Migrating custom_hooks...")
        await migrate_custom_hooks(sqlite_session, mongodb)

        # Migrate project_hooks
        print("\n5. Migrating project_hooks...")
        await migrate_project_hooks(sqlite_session, mongodb)

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


async def migrate_default_hooks(sqlite_session, mongodb):
    """Migrate default_hooks table."""
    # Check if already migrated
    existing_count = await mongodb.default_hooks.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ default_hooks already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_hooks migration")
            return
        await mongodb.default_hooks.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM default_hooks"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No default_hooks to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        doc = {
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "General"),
            "hook_config": row_dict.get("hook_config"),
            "setup_instructions": row_dict.get("setup_instructions"),
            "dependencies": row_dict.get("dependencies"),
            "script_file": row_dict.get("script_file"),
            "is_active": bool(row_dict.get("is_active", True)),
            "is_favorite": bool(row_dict.get("is_favorite", False)),
            "created_at": row_dict.get("created_at") or datetime.utcnow(),
            "updated_at": row_dict.get("updated_at") or datetime.utcnow(),
            "_sqlite_id": row_dict["id"]  # Keep reference to original ID
        }
        documents.append(doc)

    # Insert to MongoDB
    result = await mongodb.default_hooks.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} default_hooks")


async def migrate_custom_hooks(sqlite_session, mongodb):
    """Migrate custom_hooks table."""
    # Check if already migrated
    existing_count = await mongodb.custom_hooks.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ custom_hooks already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping custom_hooks migration")
            return
        await mongodb.custom_hooks.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM custom_hooks"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No custom_hooks to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        doc = {
            "project_id": row_dict["project_id"],
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "Custom"),
            "file_name": row_dict.get("file_name"),
            "hook_config": row_dict.get("hook_config"),
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
    result = await mongodb.custom_hooks.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} custom_hooks")


async def migrate_project_hooks(sqlite_session, mongodb):
    """Migrate project_hooks junction table."""
    # Check if already migrated
    existing_count = await mongodb.project_hooks.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ project_hooks already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping project_hooks migration")
            return
        await mongodb.project_hooks.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM project_hooks"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No project_hooks to migrate")
        return

    # Build ID mapping from SQLite ID to MongoDB ObjectId
    default_id_map = await build_id_map(mongodb.default_hooks)
    custom_id_map = await build_id_map(mongodb.custom_hooks)

    # Convert to MongoDB documents
    documents = []
    skipped = 0
    for row in rows:
        row_dict = dict(zip(columns, row))
        hook_type = row_dict["hook_type"]
        sqlite_hook_id = row_dict["hook_id"]

        # Map SQLite ID to MongoDB ObjectId
        if hook_type == "default":
            mongo_hook_id = default_id_map.get(sqlite_hook_id)
        else:
            mongo_hook_id = custom_id_map.get(sqlite_hook_id)

        if not mongo_hook_id:
            print(f"   ⚠ Skipping: hook_id={sqlite_hook_id} ({hook_type}) not found in MongoDB")
            skipped += 1
            continue

        doc = {
            "project_id": row_dict["project_id"],
            "hook_id": str(mongo_hook_id),  # Store as string for consistency
            "hook_type": hook_type,
            "enabled_at": row_dict.get("enabled_at") or datetime.utcnow(),
            "enabled_by": row_dict.get("enabled_by", "user")
        }
        documents.append(doc)

    # Insert to MongoDB
    if documents:
        result = await mongodb.project_hooks.insert_many(documents)
        print(f"   ✓ Migrated {len(result.inserted_ids)} project_hooks")
    if skipped:
        print(f"   ⚠ Skipped {skipped} records (hook not found)")


async def build_id_map(collection):
    """Build mapping from SQLite ID to MongoDB ObjectId."""
    id_map = {}
    cursor = collection.find({}, {"_id": 1, "_sqlite_id": 1})
    async for doc in cursor:
        if "_sqlite_id" in doc:
            id_map[doc["_sqlite_id"]] = doc["_id"]
    return id_map


async def create_indexes(mongodb):
    """Create MongoDB indexes for hook collections."""
    # Default hooks indexes
    await mongodb.default_hooks.create_index("name", unique=True)
    await mongodb.default_hooks.create_index("is_active")
    await mongodb.default_hooks.create_index("is_favorite")
    await mongodb.default_hooks.create_index("category")
    print("   ✓ default_hooks indexes created")

    # Custom hooks indexes
    await mongodb.custom_hooks.create_index("project_id")
    await mongodb.custom_hooks.create_index([("project_id", 1), ("name", 1)], unique=True)
    await mongodb.custom_hooks.create_index("is_favorite")
    await mongodb.custom_hooks.create_index("status")
    print("   ✓ custom_hooks indexes created")

    # Project hooks indexes
    await mongodb.project_hooks.create_index("project_id")
    await mongodb.project_hooks.create_index([
        ("project_id", 1),
        ("hook_id", 1),
        ("hook_type", 1)
    ], unique=True)
    print("   ✓ project_hooks indexes created")


if __name__ == "__main__":
    asyncio.run(migrate_hooks())
