"""
Migration script: Migrate Skills from SQLite to MongoDB

This script migrates:
- default_skills table → default_skills collection
- custom_skills table → custom_skills collection
- project_skills table → project_skills collection

Usage:
    cd claudetask/backend
    python -m migrations.migrate_skills_to_mongodb
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


async def migrate_skills():
    """Main migration function."""
    print("=" * 60)
    print("Skills Migration: SQLite → MongoDB")
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

        # Migrate default_skills
        print("\n3. Migrating default_skills...")
        await migrate_default_skills(sqlite_session, mongodb)

        # Migrate custom_skills
        print("\n4. Migrating custom_skills...")
        await migrate_custom_skills(sqlite_session, mongodb)

        # Migrate project_skills
        print("\n5. Migrating project_skills...")
        await migrate_project_skills(sqlite_session, mongodb)

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


async def migrate_default_skills(sqlite_session, mongodb):
    """Migrate default_skills table."""
    # Check if already migrated
    existing_count = await mongodb.default_skills.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ default_skills already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_skills migration")
            return
        await mongodb.default_skills.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM default_skills"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No default_skills to migrate")
        return

    # Convert to MongoDB documents
    documents = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        doc = {
            "name": row_dict["name"],
            "description": row_dict["description"],
            "category": row_dict.get("category", "General"),
            "file_name": row_dict["file_name"],
            "content": row_dict.get("content"),
            "skill_metadata": row_dict.get("skill_metadata"),
            "is_active": bool(row_dict.get("is_active", True)),
            "is_favorite": bool(row_dict.get("is_favorite", False)),
            "created_at": row_dict.get("created_at") or datetime.utcnow(),
            "updated_at": row_dict.get("updated_at") or datetime.utcnow(),
            "_sqlite_id": row_dict["id"]  # Keep reference to original ID
        }
        documents.append(doc)

    # Insert to MongoDB
    result = await mongodb.default_skills.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} default_skills")


async def migrate_custom_skills(sqlite_session, mongodb):
    """Migrate custom_skills table."""
    # Check if already migrated
    existing_count = await mongodb.custom_skills.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ custom_skills already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping custom_skills migration")
            return
        await mongodb.custom_skills.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM custom_skills"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No custom_skills to migrate")
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
            "file_name": row_dict["file_name"],
            "content": row_dict.get("content"),
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
    result = await mongodb.custom_skills.insert_many(documents)
    print(f"   ✓ Migrated {len(result.inserted_ids)} custom_skills")


async def migrate_project_skills(sqlite_session, mongodb):
    """Migrate project_skills junction table."""
    # Check if already migrated
    existing_count = await mongodb.project_skills.count_documents({})
    if existing_count > 0:
        print(f"   ⚠ project_skills already has {existing_count} documents")
        response = input("   Do you want to drop and re-migrate? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping project_skills migration")
            return
        await mongodb.project_skills.delete_many({})
        print("   Dropped existing documents")

    # Fetch from SQLite
    result = sqlite_session.execute(text("SELECT * FROM project_skills"))
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        print("   No project_skills to migrate")
        return

    # Build ID mapping from SQLite ID to MongoDB ObjectId
    default_id_map = await build_id_map(mongodb.default_skills)
    custom_id_map = await build_id_map(mongodb.custom_skills)

    # Convert to MongoDB documents
    documents = []
    skipped = 0
    for row in rows:
        row_dict = dict(zip(columns, row))
        skill_type = row_dict["skill_type"]
        sqlite_skill_id = row_dict["skill_id"]

        # Map SQLite ID to MongoDB ObjectId
        if skill_type == "default":
            mongo_skill_id = default_id_map.get(sqlite_skill_id)
        else:
            mongo_skill_id = custom_id_map.get(sqlite_skill_id)

        if not mongo_skill_id:
            print(f"   ⚠ Skipping: skill_id={sqlite_skill_id} ({skill_type}) not found in MongoDB")
            skipped += 1
            continue

        doc = {
            "project_id": row_dict["project_id"],
            "skill_id": str(mongo_skill_id),  # Store as string for consistency
            "skill_type": skill_type,
            "enabled_at": row_dict.get("enabled_at") or datetime.utcnow(),
            "enabled_by": row_dict.get("enabled_by", "user")
        }
        documents.append(doc)

    # Insert to MongoDB
    if documents:
        result = await mongodb.project_skills.insert_many(documents)
        print(f"   ✓ Migrated {len(result.inserted_ids)} project_skills")
    if skipped:
        print(f"   ⚠ Skipped {skipped} records (skill not found)")


async def build_id_map(collection):
    """Build mapping from SQLite ID to MongoDB ObjectId."""
    id_map = {}
    cursor = collection.find({}, {"_id": 1, "_sqlite_id": 1})
    async for doc in cursor:
        if "_sqlite_id" in doc:
            id_map[doc["_sqlite_id"]] = doc["_id"]
    return id_map


async def create_indexes(mongodb):
    """Create MongoDB indexes for skill collections."""
    # Default skills indexes
    await mongodb.default_skills.create_index("name", unique=True)
    await mongodb.default_skills.create_index("is_active")
    await mongodb.default_skills.create_index("is_favorite")
    await mongodb.default_skills.create_index("category")
    print("   ✓ default_skills indexes created")

    # Custom skills indexes
    await mongodb.custom_skills.create_index("project_id")
    await mongodb.custom_skills.create_index([("project_id", 1), ("name", 1)], unique=True)
    await mongodb.custom_skills.create_index("is_favorite")
    await mongodb.custom_skills.create_index("status")
    print("   ✓ custom_skills indexes created")

    # Project skills indexes
    await mongodb.project_skills.create_index("project_id")
    await mongodb.project_skills.create_index([
        ("project_id", 1),
        ("skill_id", 1),
        ("skill_type", 1)
    ], unique=True)
    print("   ✓ project_skills indexes created")


if __name__ == "__main__":
    asyncio.run(migrate_skills())
