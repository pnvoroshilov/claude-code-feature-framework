#!/usr/bin/env python3
"""
Migration 002: Remove deprecated manual_testing_mode and manual_review_mode fields.
Keeps only manual_mode as single source of truth for workflow mode.

Run: python migrations/002_remove_deprecated_manual_fields.py
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    """Remove deprecated manual_testing_mode and manual_review_mode columns."""

    # Path to database
    db_path = Path(__file__).parent.parent / "data" / "claudetask.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the columns still exist
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = [col[1] for col in cursor.fetchall()]

        if "manual_testing_mode" not in columns and "manual_review_mode" not in columns:
            print("✅ Migration already applied - deprecated columns not found")
            return True

        print("🔄 Starting migration to remove deprecated manual mode fields...")

        # Step 1: Create new table without deprecated fields
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
        print("✅ Created new table structure")

        # Step 2: Copy data (only keeping manual_mode)
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
        print(f"✅ Migrated {cursor.rowcount} project settings")

        # Step 3: Drop old table
        cursor.execute("DROP TABLE project_settings")
        print("✅ Dropped old table")

        # Step 4: Rename new table
        cursor.execute("ALTER TABLE project_settings_new RENAME TO project_settings")
        print("✅ Renamed new table")

        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully")

        # Verify
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Final columns: {', '.join(columns)}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)