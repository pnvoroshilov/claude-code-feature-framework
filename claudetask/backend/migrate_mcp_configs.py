#!/usr/bin/env python
"""
Database migration script to make MCP configs project-specific
Changes:
1. Make custom_mcp_configs.project_id NOT NULL
2. Remove unique constraint on name (make it unique per project instead)
3. Add composite unique constraint on (project_id, name)
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Migrate MCP configs to be project-specific"""
    db_path = Path(__file__).parent / "data" / "claudetask.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("Starting MCP configs migration...")

        # Step 1: Check if custom_mcp_configs table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='custom_mcp_configs'
        """)
        if not cursor.fetchone():
            print("Table 'custom_mcp_configs' does not exist yet. Nothing to migrate.")
            conn.close()
            return True

        # Step 2: Check current table structure
        cursor.execute("PRAGMA table_info(custom_mcp_configs)")
        columns = cursor.fetchall()
        print(f"Current columns: {[col[1] for col in columns]}")

        # Step 3: Create backup of existing data
        cursor.execute("SELECT COUNT(*) FROM custom_mcp_configs")
        count = cursor.fetchone()[0]
        print(f"Found {count} existing MCP configs")

        if count > 0:
            # Backup existing data
            cursor.execute("""
                CREATE TEMPORARY TABLE custom_mcp_configs_backup AS
                SELECT * FROM custom_mcp_configs
            """)
            print("Created backup of existing data")

            # Check if any configs have NULL project_id
            cursor.execute("SELECT COUNT(*) FROM custom_mcp_configs WHERE project_id IS NULL")
            null_count = cursor.fetchone()[0]

            if null_count > 0:
                print(f"WARNING: Found {null_count} MCP configs with NULL project_id")
                print("These configs will be deleted as they cannot be assigned to a specific project.")
                print("Please reassign them manually if needed.")

                # Show the configs that will be deleted
                cursor.execute("SELECT id, name, description FROM custom_mcp_configs WHERE project_id IS NULL")
                null_configs = cursor.fetchall()
                for cfg in null_configs:
                    print(f"  - ID: {cfg[0]}, Name: {cfg[1]}, Description: {cfg[2]}")

        # Step 4: Create new table with correct schema
        print("Creating new table with project-specific schema...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_mcp_configs_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id VARCHAR NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(50) NOT NULL,
                config JSON NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                error_message TEXT,
                created_by VARCHAR(100) DEFAULT 'user',
                is_favorite BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id),
                UNIQUE(project_id, name)
            )
        """)
        print("Created new table schema")

        # Step 5: Copy data (only records with valid project_id)
        if count > 0:
            cursor.execute("""
                INSERT INTO custom_mcp_configs_new
                (id, project_id, name, description, category, config, status, error_message,
                 created_by, is_favorite, created_at, updated_at)
                SELECT id, project_id, name, description, category, config, status, error_message,
                       created_by, is_favorite, created_at, updated_at
                FROM custom_mcp_configs_backup
                WHERE project_id IS NOT NULL
            """)

            migrated_count = cursor.rowcount
            print(f"Migrated {migrated_count} MCP configs with valid project_id")

        # Step 6: Drop old table and rename new one
        cursor.execute("DROP TABLE custom_mcp_configs")
        cursor.execute("ALTER TABLE custom_mcp_configs_new RENAME TO custom_mcp_configs")
        print("Replaced old table with new schema")

        # Step 7: Commit changes
        conn.commit()
        print("Migration completed successfully!")

        # Verify the new schema
        cursor.execute("PRAGMA table_info(custom_mcp_configs)")
        new_columns = cursor.fetchall()
        print(f"New schema columns: {[col[1] for col in new_columns]}")

        # Check project_id is now NOT NULL
        project_id_col = next((col for col in new_columns if col[1] == 'project_id'), None)
        if project_id_col:
            is_nullable = project_id_col[3] == 0  # notnull flag
            if is_nullable:
                print("ERROR: project_id is still nullable")
                return False
            else:
                print("✓ Verified: project_id is now NOT NULL")

        # Verify unique constraint
        cursor.execute("PRAGMA index_list(custom_mcp_configs)")
        indexes = cursor.fetchall()
        print(f"Indexes: {indexes}")

        cursor.execute("SELECT COUNT(*) FROM custom_mcp_configs")
        final_count = cursor.fetchone()[0]
        print(f"Final count: {final_count} MCP configs")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Configs Migration: Making configs project-specific")
    print("=" * 60)
    success = migrate_database()
    sys.exit(0 if success else 1)
