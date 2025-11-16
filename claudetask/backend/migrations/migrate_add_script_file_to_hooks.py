"""
Migration script to add script_file column to hooks tables
Run this script to update existing database with script file support
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def migrate():
    """Add script_file column to hooks tables"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(default_hooks)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'script_file' in columns:
            print("✓ script_file column already exists. No migration needed.")
            return

        # Read and execute SQL migration file
        sql_file = Path(__file__).parent / "004_add_script_file_to_hooks.sql"
        with open(sql_file, 'r') as f:
            sql_script = f.read()

        print("Adding script_file column to hooks tables...")
        cursor.executescript(sql_script)

        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"  - Added script_file column to default_hooks")
        print(f"  - Added script_file column to custom_hooks")

    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
