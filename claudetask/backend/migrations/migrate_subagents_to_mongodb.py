"""
Migration script: Migrate Subagents from SQLite to MongoDB

This script migrates:
- default_subagents table → default_subagents collection
- custom_subagents table → custom_subagents collection
- project_subagents table → project_subagents collection
- subagent_skills table → subagent_skills collection

Usage:
    cd claudetask/backend
    python -m migrations.migrate_subagents_to_mongodb
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


async def migrate_subagents():
    """Main migration function."""
    print("=" * 60)
    print("Subagents Migration: SQLite → MongoDB")
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

        # Migrate default_subagents
        print("\n3. Migrating default_subagents...")
        await migrate_default_subagents(sqlite_session, mongodb)

        # Migrate custom_subagents
        print("\n4. Migrating custom_subagents...")
        await migrate_custom_subagents(sqlite_session, mongodb)

        # Migrate project_subagents
        print("\n5. Migrating project_subagents...")
        await migrate_project_subagents(sqlite_session, mongodb)

        # Migrate subagent_skills
        print("\n6. Migrating subagent_skills...")
        await migrate_subagent_skills(sqlite_session, mongodb)

        # Create indexes
        print("\n7. Creating indexes...")
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


async def migrate_default_subagents(sqlite_session, mongodb):
    """Migrate default_subagents table."""
    # Check if already migrated
    existing_count = await mongodb.default_subagents.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ default_subagents already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_subagents migration")
            return
        await mongodb.default_subagents.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM default_subagents"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No default_subagents to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))

        # Parse tools JSON if stored as string
        tools = row_dict.get("tools")
        if isinstance(tools, str):
            try:
                tools = json.loads(tools)
            except:
                tools = []

        doc = {
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "General"),
            "tools": tools or [],
            "system_prompt": row_dict.get("system_prompt"),
            "model": row_dict.get("model"),
            "file_name": row_dict.get("file_name"),
            "is_active": bool(row_dict.get("is_active", True)),
            "is_favorite": bool(row_dict.get("is_favorite", False)),
            "created_at": row_dict.get("created_at") or datetime.utcnow(),
            "updated_at": row_dict.get("updated_at") or datetime.utcnow(),
            "_sqlite_id": row_dict["id"]  # Keep reference to original ID
        }
        documents.append(doc)

    # Insert to MongoDB
    result = await mongodb.default_subagents.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} default_subagents")


async def migrate_custom_subagents(sqlite_session, mongodb):
    """Migrate custom_subagents table."""
    # Check if already migrated
    existing_count = await mongodb.custom_subagents.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ custom_subagents already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping custom_subagents migration")
            return
        await mongodb.custom_subagents.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM custom_subagents"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No custom_subagents to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))

        # Parse tools JSON if stored as string
        tools = row_dict.get("tools")
        if isinstance(tools, str):
            try:
                tools = json.loads(tools)
            except:
                tools = []

        doc = {
            "project_id": row_dict["project_id"],
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "Custom"),
            "tools": tools or [],
            "system_prompt": row_dict.get("system_prompt"),
            "model": row_dict.get("model"),
            "file_name": row_dict.get("file_name"),
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
    result = await mongodb.custom_subagents.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} custom_subagents")


async def migrate_project_subagents(sqlite_session, mongodb):
    """Migrate project_subagents junction table."""
    # Check if already migrated
    existing_count = await mongodb.project_subagents.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ project_subagents already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping project_subagents migration")
            return
        await mongodb.project_subagents.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM project_subagents"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No project_subagents to migrate")
        return

    # Build ID mapping from SQLite ID to MongoDB ObjectId
    default_id_map = await build_id_map(mongodb.default_subagents)
    custom_id_map = await build_id_map(mongodb.custom_subagents)

    # Convert to MongoDB documents
    documents = []
    skipped = 0
    for row in rows:
        row_dict = dict(zip(columns, row))
        subagent_type = row_dict["subagent_type"]
        sqlite_subagent_id = row_dict["subagent_id"]

        # Map SQLite ID to MongoDB ObjectId
        if subagent_type == "default":
            mongo_subagent_id = default_id_map.get(sqlite_subagent_id)
        else:
            mongo_subagent_id = custom_id_map.get(sqlite_subagent_id)

        if not mongo_subagent_id:
            print(f"   ⚠ Skipping: subagent_id={sqlite_subagent_id} ({subagent_type}) not found in MongoDB")
            skipped += 1
            continue

        doc = {
            "project_id": row_dict["project_id"],
            "subagent_id": str(mongo_subagent_id),  # Store as string for consistency
            "subagent_type": subagent_type,
            "enabled_at": row_dict.get("enabled_at") or datetime.utcnow(),
            "enabled_by": row_dict.get("enabled_by", "user")
        }
        documents.append(doc)

    # Insert to MongoDB
    if documents:
        result = await mongodb.project_subagents.insert_many(documents)
        print(f"   ✓ Migrated {len(result.inserted_ids)} project_subagents")
    if skipped:
        print(f"   ⚠ Skipped {skipped} records (subagent not found)")


async def migrate_subagent_skills(sqlite_session, mongodb):
    """Migrate subagent_skills junction table."""
    # Check if already migrated
    existing_count = await mongodb.subagent_skills.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ subagent_skills already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping subagent_skills migration")
            return
        await mongodb.subagent_skills.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    try:
        result = sqlite_session.execute(text("SELECT * FROM subagent_skills"))
        rows = result.fetchall()
        columns = result.keys()
    except Exception as e:
        print(f"   ⚠ subagent_skills table not found: {e}")
        print("   Skipping subagent_skills migration")
        return

    if not rows:
        print("   No subagent_skills to migrate")
        return

    # Build ID mappings
    default_subagent_id_map = await build_id_map(mongodb.default_subagents)
    custom_subagent_id_map = await build_id_map(mongodb.custom_subagents)
    default_skill_id_map = await build_id_map(mongodb.default_skills)
    custom_skill_id_map = await build_id_map(mongodb.custom_skills)

    # Convert to MongoDB documents
    documents = []
    skipped = 0
    for row in rows:
        row_dict = dict(zip(columns, row))

        subagent_type = row_dict["subagent_type"]
        sqlite_subagent_id = row_dict["subagent_id"]
        skill_type = row_dict["skill_type"]
        sqlite_skill_id = row_dict["skill_id"]

        # Map subagent SQLite ID to MongoDB ObjectId
        if subagent_type == "default":
            mongo_subagent_id = default_subagent_id_map.get(sqlite_subagent_id)
        else:
            mongo_subagent_id = custom_subagent_id_map.get(sqlite_subagent_id)

        # Map skill SQLite ID to MongoDB ObjectId
        if skill_type == "default":
            mongo_skill_id = default_skill_id_map.get(sqlite_skill_id)
        else:
            mongo_skill_id = custom_skill_id_map.get(sqlite_skill_id)

        if not mongo_subagent_id:
            print(f"   ⚠ Skipping: subagent_id={sqlite_subagent_id} ({subagent_type}) not found")
            skipped += 1
            continue

        if not mongo_skill_id:
            print(f"   ⚠ Skipping: skill_id={sqlite_skill_id} ({skill_type}) not found")
            skipped += 1
            continue

        doc = {
            "subagent_id": str(mongo_subagent_id),
            "subagent_type": subagent_type,
            "skill_id": str(mongo_skill_id),
            "skill_type": skill_type,
            "assigned_at": row_dict.get("assigned_at") or datetime.utcnow()
        }
        documents.append(doc)

    # Insert to MongoDB
    if documents:
        result = await mongodb.subagent_skills.insert_many(documents)
        print(f"   ✓ Migrated {len(result.inserted_ids)} subagent_skills")
    if skipped:
        print(f"   ⚠ Skipped {skipped} records (subagent or skill not found)")


async def build_id_map(collection):
    """Build mapping from SQLite ID to MongoDB ObjectId."""
    id_map = {}
    cursor = collection.find({}, {"_id": 1, "_sqlite_id": 1})
    async for doc in cursor:
        if "_sqlite_id" in doc:
            id_map[doc["_sqlite_id"]] = doc["_id"]
    return id_map


async def create_indexes(mongodb):
    """Create MongoDB indexes for subagent collections."""
    # Default subagents indexes
    await mongodb.default_subagents.create_index("name", unique=True)
    await mongodb.default_subagents.create_index("is_active")
    await mongodb.default_subagents.create_index("is_favorite")
    await mongodb.default_subagents.create_index("category")
    print("   ✓ default_subagents indexes created")

    # Custom subagents indexes
    await mongodb.custom_subagents.create_index("project_id")
    await mongodb.custom_subagents.create_index([("project_id", 1), ("name", 1)], unique=True)
    await mongodb.custom_subagents.create_index("is_favorite")
    await mongodb.custom_subagents.create_index("status")
    print("   ✓ custom_subagents indexes created")

    # Project subagents indexes
    await mongodb.project_subagents.create_index("project_id")
    await mongodb.project_subagents.create_index([
        ("project_id", 1),
        ("subagent_id", 1),
        ("subagent_type", 1)
    ], unique=True)
    print("   ✓ project_subagents indexes created")

    # Subagent skills indexes
    await mongodb.subagent_skills.create_index("subagent_id")
    await mongodb.subagent_skills.create_index([
        ("subagent_id", 1),
        ("subagent_type", 1),
        ("skill_id", 1),
        ("skill_type", 1)
    ], unique=True)
    print("   ✓ subagent_skills indexes created")


if __name__ == "__main__":
    asyncio.run(migrate_subagents())
