"""
Update Post-Merge Documentation hook with script_file
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def update_hook():
    """Update Post-Merge Documentation hook to add script_file"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Update the Post-Merge Documentation Update hook
        cursor.execute("""
            UPDATE default_hooks
            SET script_file = 'post-push-docs.sh'
            WHERE name = 'Post-Merge Documentation Update'
        """)

        if cursor.rowcount > 0:
            print(f"✓ Updated {cursor.rowcount} hook(s)")
            conn.commit()
            print("✓ Post-Merge Documentation Update hook now includes script_file: post-push-docs.sh")
        else:
            print("⚠ No hook found with name 'Post-Merge Documentation Update'")

    except sqlite3.Error as e:
        print(f"✗ Update failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    update_hook()
