"""
Add post-merge-documentation hook to default_hooks table
"""
import sqlite3
import json
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def add_hook():
    """Add post-merge-documentation hook if it doesn't exist"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if hook already exists
        cursor.execute("SELECT id FROM default_hooks WHERE file_name = 'post-merge-documentation.json'")
        if cursor.fetchone():
            print("✓ Post-merge documentation hook already exists")
            return

        # Load hook from JSON file
        hook_file = Path(__file__).parent.parent.parent.parent / "framework-assets" / "claude-hooks" / "post-merge-documentation.json"

        if not hook_file.exists():
            print(f"✗ Hook file not found: {hook_file}")
            return

        with open(hook_file, 'r') as f:
            hook_data = json.load(f)

        # Insert hook into database
        cursor.execute('''
            INSERT INTO default_hooks (name, description, category, file_name, hook_config,
                                      setup_instructions, dependencies, is_active, is_favorite,
                                      created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            hook_data['name'],
            hook_data['description'],
            hook_data['category'],
            'post-merge-documentation.json',
            json.dumps(hook_data['hook_config']),
            hook_data.get('setup_instructions', ''),
            json.dumps(hook_data.get('dependencies', []))
        ))

        conn.commit()
        print("✓ Successfully added post-merge-documentation hook to database")
        print(f"  - Name: {hook_data['name']}")
        print(f"  - Category: {hook_data['category']}")
        print(f"  - Status: Active")

    except sqlite3.Error as e:
        print(f"✗ Failed to add hook: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    add_hook()
