"""
Migration script to add conversation memory tables
Run this script to enable cross-session memory persistence
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def migrate():
    """Create memory-related tables for conversation persistence"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_memory'")
        if cursor.fetchone():
            print("✓ Memory tables already exist. No migration needed.")
            return

        # Read and execute SQL migration file
        sql_file = Path(__file__).parent / "009_add_memory_tables.sql"
        with open(sql_file, 'r') as f:
            sql_script = f.read()

        print("Creating memory tables...")
        cursor.executescript(sql_script)

        # Create initial project summary for existing active projects
        print("Initializing project summaries for existing projects...")
        cursor.execute("""
            INSERT INTO project_summaries (project_id, summary, key_decisions, tech_stack, patterns, gotchas)
            SELECT
                id as project_id,
                'Project initialized. No summary available yet.' as summary,
                '[]' as key_decisions,
                '[]' as tech_stack,
                '[]' as patterns,
                '[]' as gotchas
            FROM projects
            WHERE is_active = 1
        """)

        rows_affected = cursor.rowcount
        if rows_affected > 0:
            print(f"✓ Created initial summaries for {rows_affected} active project(s)")

        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"  - Created conversation_memory table")
        print(f"  - Created project_summaries table")
        print(f"  - Created memory_rag_status table")
        print(f"  - Created memory_sessions table")
        print(f"  - Created all necessary indexes")
        if rows_affected > 0:
            print(f"  - Initialized summaries for {rows_affected} project(s)")

    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()