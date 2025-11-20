#!/usr/bin/env python3
"""
Migration 006: Add CASCADE DELETE to foreign keys

SQLite doesn't support altering foreign keys directly.
We need to recreate tables with proper CASCADE DELETE constraints.
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Get database path"""
    backend_dir = Path(__file__).parent.parent
    return backend_dir / "data" / "claudetask.db"

def migrate():
    """Add CASCADE DELETE to all foreign key constraints"""
    db_path = get_db_path()

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")

        # Start transaction
        cursor.execute("BEGIN TRANSACTION")

        # First, clean up orphaned records (records referencing non-existent projects)
        print("🧹 Cleaning up orphaned records...")

        # Get list of valid project IDs
        cursor.execute("SELECT id FROM projects")
        valid_project_ids = {row[0] for row in cursor.fetchall()}
        valid_project_ids_str = "', '".join(valid_project_ids) if valid_project_ids else ""

        if valid_project_ids:
            # Delete orphaned records from all tables
            orphan_tables = [
                'tasks', 'agents', 'project_settings', 'custom_skills',
                'custom_subagents', 'project_skills', 'project_mcp_configs',
                'custom_mcp_configs', 'custom_hooks', 'project_hooks',
                'project_subagents', 'claude_sessions'
            ]

            for table in orphan_tables:
                cursor.execute(f"""
                    DELETE FROM {table}
                    WHERE project_id NOT IN ('{valid_project_ids_str}')
                """)
                deleted = cursor.rowcount
                if deleted > 0:
                    print(f"   Deleted {deleted} orphaned records from {table}")

        print("\n🔄 Recreating tables with CASCADE DELETE...")

        # List of tables that need CASCADE DELETE (all tables with project_id FK)
        tables_to_migrate = [
            'tasks',
            'agents',
            'project_settings',
            'custom_skills',
            'custom_subagents',
            'project_skills',
            'project_mcp_configs',
            'custom_mcp_configs',
            'custom_hooks',
            'project_hooks',
            'project_subagents',
            'claude_sessions'
        ]

        for table_name in tables_to_migrate:
            print(f"   Migrating {table_name}...")

            # Get table schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            result = cursor.fetchone()

            if not result:
                print(f"   ⚠️  Table {table_name} not found, skipping")
                continue

            create_sql = result[0]

            # Replace all ForeignKey references to projects.id with CASCADE DELETE
            # Pattern: FOREIGN KEY (project_id) REFERENCES projects (id)
            # Replace with: FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            new_create_sql = create_sql.replace(
                'REFERENCES projects (id)',
                'REFERENCES projects (id) ON DELETE CASCADE'
            )

            # Skip if already has CASCADE
            if create_sql == new_create_sql:
                print(f"   ✓ {table_name} already has CASCADE DELETE")
                continue

            # Rename old table
            cursor.execute(f"ALTER TABLE {table_name} RENAME TO {table_name}_old")

            # Create new table with CASCADE DELETE
            cursor.execute(new_create_sql)

            # Copy data from old table to new table
            cursor.execute(f"SELECT * FROM {table_name}_old LIMIT 1")
            columns = [description[0] for description in cursor.description]
            columns_str = ', '.join(columns)

            cursor.execute(f"""
                INSERT INTO {table_name} ({columns_str})
                SELECT {columns_str} FROM {table_name}_old
            """)

            # Drop old table
            cursor.execute(f"DROP TABLE {table_name}_old")

            print(f"   ✓ {table_name} migrated successfully")

        # Commit transaction
        conn.commit()

        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")

        # Verify foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()

        if fk_errors:
            print(f"❌ Foreign key constraint errors detected:")
            for error in fk_errors:
                print(f"   {error}")
            return

        print("\n✅ Migration 006 completed successfully!")
        print("✅ All foreign keys now have CASCADE DELETE")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
