"""
Migration: Add worktree_enabled field to project_settings table
Date: 2025-11-20
"""

import sqlite3
import os

def migrate():
    """Add worktree_enabled column to project_settings table"""
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "claudetask.db")

    # Ensure database file exists
    if not os.path.exists(db_path):
        print(f"✗ Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'worktree_enabled' in columns:
            print("✓ Column 'worktree_enabled' already exists. No migration needed.")
            return True

        # Add column
        print("Adding 'worktree_enabled' column to project_settings table...")
        cursor.execute("ALTER TABLE project_settings ADD COLUMN worktree_enabled BOOLEAN DEFAULT 1 NOT NULL")

        # Update existing project settings to have worktree_enabled = true (1)
        cursor.execute("UPDATE project_settings SET worktree_enabled = 1 WHERE worktree_enabled IS NULL")

        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"✓ All existing project settings set to worktree_enabled = true by default")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
