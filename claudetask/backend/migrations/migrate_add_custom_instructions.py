"""
Migration script to add custom_instructions field to projects table
Run this script to update existing database with the new field
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def migrate():
    """Add custom_instructions column to projects table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'custom_instructions' in columns:
            print("✓ Column 'custom_instructions' already exists. No migration needed.")
            return

        print("Adding custom_instructions column to projects table...")
        cursor.execute("ALTER TABLE projects ADD COLUMN custom_instructions TEXT DEFAULT ''")

        # Update existing records
        cursor.execute("UPDATE projects SET custom_instructions = '' WHERE custom_instructions IS NULL")

        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"  - Added custom_instructions column")
        print(f"  - Updated {cursor.rowcount} existing records")

    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
