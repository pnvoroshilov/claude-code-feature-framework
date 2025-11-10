#!/usr/bin/env python
"""
Database migration script to add subagent tables
"""
import sqlite3
import json
import sys
from pathlib import Path

def migrate_database():
    """Create subagent tables if they don't exist"""
    db_path = Path(__file__).parent / "data" / "claudetask.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]

        tables_created = []

        # Create default_subagents table
        if 'default_subagents' not in existing_tables:
            print("Creating 'default_subagents' table...")
            cursor.execute("""
                CREATE TABLE default_subagents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    subagent_type VARCHAR(100) NOT NULL,
                    tools_available TEXT,
                    recommended_for TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            tables_created.append('default_subagents')
        else:
            print("Table 'default_subagents' already exists")

        # Create custom_subagents table
        if 'custom_subagents' not in existing_tables:
            print("Creating 'custom_subagents' table...")
            cursor.execute("""
                CREATE TABLE custom_subagents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id VARCHAR NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    subagent_type VARCHAR(100) NOT NULL,
                    config TEXT NOT NULL,
                    tools_available TEXT,
                    status VARCHAR(20) DEFAULT 'active',
                    error_message TEXT,
                    created_by VARCHAR(100) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """)
            tables_created.append('custom_subagents')
        else:
            print("Table 'custom_subagents' already exists")

        # Create project_subagents table (junction table)
        if 'project_subagents' not in existing_tables:
            print("Creating 'project_subagents' table...")
            cursor.execute("""
                CREATE TABLE project_subagents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id VARCHAR NOT NULL,
                    subagent_id INTEGER NOT NULL,
                    subagent_type VARCHAR(10) NOT NULL,
                    enabled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    enabled_by VARCHAR(100) DEFAULT 'user',
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """)
            tables_created.append('project_subagents')
        else:
            print("Table 'project_subagents' already exists")

        if not tables_created:
            print("All subagent tables already exist")
            conn.close()
            return True

        conn.commit()
        print("Migration completed successfully!")

        # Verify the tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]

        for table in tables_created:
            if table in existing_tables:
                print(f"Verification: Table '{table}' has been created successfully")
            else:
                print(f"ERROR: Table '{table}' was not created properly")
                conn.close()
                return False

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
