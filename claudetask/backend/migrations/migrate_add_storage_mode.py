"""
Migration: Add storage_mode column to project_settings table
Date: 2025-11-26
Description: Enables per-project storage mode selection (local vs mongodb)
             - 'local': SQLite + ChromaDB with all-MiniLM-L6-v2 embeddings (384d)
             - 'mongodb': MongoDB Atlas + Vector Search with voyage-3-large embeddings (1024d)
"""

import sqlite3
import os


def migrate():
    """Add storage_mode column to project_settings table"""
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "claudetask.db")

    # Ensure database file exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_done = []

        # Add storage_mode column
        if 'storage_mode' not in columns:
            print("Adding 'storage_mode' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN storage_mode TEXT NOT NULL DEFAULT 'local'")
            migrations_done.append('storage_mode')

            # Update any null values to 'local'
            cursor.execute("UPDATE project_settings SET storage_mode = 'local' WHERE storage_mode IS NULL OR storage_mode = ''")

            # Create index for faster lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_settings_storage_mode ON project_settings(storage_mode)")
            print("Created index idx_project_settings_storage_mode")
        else:
            print("Column 'storage_mode' already exists.")

        conn.commit()

        if migrations_done:
            print(f"Migration completed successfully! Added columns: {', '.join(migrations_done)}")

            # Verify migration
            cursor.execute("""
                SELECT COUNT(*) as total_projects,
                       SUM(CASE WHEN storage_mode = 'local' THEN 1 ELSE 0 END) as local_storage,
                       SUM(CASE WHEN storage_mode = 'mongodb' THEN 1 ELSE 0 END) as mongodb_storage
                FROM project_settings
            """)
            result = cursor.fetchone()
            print(f"Verification: {result[0]} total projects, {result[1]} local, {result[2]} mongodb")
        else:
            print("No migration needed. Column 'storage_mode' already exists.")

        return True

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
