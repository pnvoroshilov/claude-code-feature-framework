"""
Migration: Add project_mode field to projects table
Date: 2025-11-12
"""

import sqlite3
import os

def migrate():
    """Add project_mode column to projects table"""
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
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'project_mode' in columns:
            print("✓ Column 'project_mode' already exists. No migration needed.")
            return True

        # Add column
        print("Adding 'project_mode' column to projects table...")
        cursor.execute("ALTER TABLE projects ADD COLUMN project_mode TEXT DEFAULT 'simple' NOT NULL")

        # Update existing projects
        cursor.execute("UPDATE projects SET project_mode = 'simple' WHERE project_mode IS NULL OR project_mode = ''")

        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"✓ All existing projects set to 'simple' mode by default")
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
