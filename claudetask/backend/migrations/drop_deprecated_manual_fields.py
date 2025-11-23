"""
Migration: Drop deprecated manual_testing_mode and manual_review_mode columns

These fields were replaced by a single manual_mode boolean that controls
both UC-04 (Testing) and UC-05 (Code Review) workflows.

This migration:
1. Creates new table without deprecated fields
2. Copies data from old table
3. Drops old table
4. Renames new table to original name
"""

import sqlite3
import os
from pathlib import Path


def get_db_path():
    """Get database path"""
    backend_dir = Path(__file__).parent.parent
    db_path = backend_dir / "data" / "claudetask.db"
    return str(db_path)


def migrate():
    """Execute migration to drop deprecated manual mode fields"""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("🔄 Starting migration: drop_deprecated_manual_fields")

        # Step 1: Create new table without deprecated fields
        print("📋 Creating new project_settings table...")
        cursor.execute("""
            CREATE TABLE project_settings_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL UNIQUE,
                auto_mode BOOLEAN DEFAULT 0,
                auto_priority_threshold TEXT DEFAULT 'HIGH',
                max_parallel_tasks INTEGER DEFAULT 3,
                test_command TEXT,
                build_command TEXT,
                lint_command TEXT,
                worktree_enabled BOOLEAN NOT NULL DEFAULT 1,
                manual_mode BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Step 2: Copy data from old table (only keeping manual_mode)
        print("📦 Copying data from old table...")
        cursor.execute("""
            INSERT INTO project_settings_new (
                id, project_id, auto_mode, auto_priority_threshold,
                max_parallel_tasks, test_command, build_command, lint_command,
                worktree_enabled, manual_mode
            )
            SELECT
                id, project_id, auto_mode, auto_priority_threshold,
                max_parallel_tasks, test_command, build_command, lint_command,
                worktree_enabled, manual_mode
            FROM project_settings
        """)

        rows_copied = cursor.rowcount
        print(f"✅ Copied {rows_copied} rows")

        # Step 3: Drop old table
        print("🗑️  Dropping old project_settings table...")
        cursor.execute("DROP TABLE project_settings")

        # Step 4: Rename new table to original name
        print("🔄 Renaming new table to project_settings...")
        cursor.execute("ALTER TABLE project_settings_new RENAME TO project_settings")

        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify schema
        print("\n📊 Verifying new schema...")
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = cursor.fetchall()

        print("\nColumns in project_settings table:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # Check that deprecated fields are gone
        column_names = [col[1] for col in columns]
        if 'manual_testing_mode' in column_names or 'manual_review_mode' in column_names:
            print("❌ ERROR: Deprecated fields still exist!")
            return False

        if 'manual_mode' not in column_names:
            print("❌ ERROR: manual_mode field is missing!")
            return False

        print("✅ Schema verification passed - only manual_mode exists")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def rollback():
    """Rollback migration (restore deprecated fields)"""
    print("⚠️  Rollback not implemented for this migration")
    print("To rollback, restore from backup or recreate table with deprecated fields")
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback()
    else:
        success = migrate()

    sys.exit(0 if success else 1)
