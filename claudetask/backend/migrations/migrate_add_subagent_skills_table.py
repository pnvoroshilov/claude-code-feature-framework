"""
Migration script to add subagent_skills junction table
Run this script to update existing database with subagent-skill relationships
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config


def migrate():
    """Create subagent_skills table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subagent_skills'")
        if cursor.fetchone():
            print("✓ subagent_skills table already exists. No migration needed.")
            return

        # Create subagent_skills junction table
        print("Creating subagent_skills table...")
        cursor.execute("""
            CREATE TABLE subagent_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subagent_id INTEGER NOT NULL,
                subagent_type VARCHAR(10) NOT NULL,  -- "default" or "custom"
                skill_id INTEGER NOT NULL,
                skill_type VARCHAR(10) NOT NULL,  -- "default" or "custom"
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                assigned_by VARCHAR(100) DEFAULT 'user',
                UNIQUE(subagent_id, subagent_type, skill_id, skill_type)
            )
        """)

        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX idx_subagent_skills_subagent
            ON subagent_skills(subagent_id, subagent_type)
        """)
        cursor.execute("""
            CREATE INDEX idx_subagent_skills_skill
            ON subagent_skills(skill_id, skill_type)
        """)

        conn.commit()
        print("✓ subagent_skills table created successfully!")

    except Exception as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
