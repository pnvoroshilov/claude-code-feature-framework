"""
Migration script to add hooks tables
Run this script to update existing database with hooks support
"""
import sqlite3
import sys
import json
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def load_default_hooks():
    """Load default hooks from framework-assets/claude-hooks"""
    hooks = []
    hooks_dir = Path(__file__).parent.parent.parent.parent / "framework-assets" / "claude-hooks"

    if not hooks_dir.exists():
        print(f"Warning: Hooks directory not found: {hooks_dir}")
        return hooks

    for hook_file in hooks_dir.glob("*.json"):
        try:
            with open(hook_file, 'r') as f:
                hook_data = json.load(f)
                hooks.append({
                    'name': hook_data['name'],
                    'description': hook_data['description'],
                    'category': hook_data['category'],
                    'file_name': hook_file.name,
                    'script_file': hook_data.get('script_file'),  # Optional separate script file
                    'hook_config': json.dumps(hook_data['hook_config']),
                    'setup_instructions': hook_data.get('setup_instructions', ''),
                    'dependencies': json.dumps(hook_data.get('dependencies', []))
                })
        except Exception as e:
            print(f"Warning: Could not load hook file {hook_file.name}: {e}")

    return hooks

def migrate():
    """Create hooks tables and populate default hooks"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='default_hooks'")
        if cursor.fetchone():
            print("✓ Hooks tables already exist. No migration needed.")
            return

        # Read and execute SQL migration file
        sql_file = Path(__file__).parent / "003_add_hooks_tables.sql"
        with open(sql_file, 'r') as f:
            sql_script = f.read()

        print("Creating hooks tables...")
        cursor.executescript(sql_script)

        # Load and insert default hooks
        print("Loading default hooks...")
        default_hooks = load_default_hooks()

        if default_hooks:
            cursor.executemany('''
                INSERT INTO default_hooks (name, description, category, file_name, script_file, hook_config,
                                          setup_instructions, dependencies, is_active, is_favorite)
                VALUES (:name, :description, :category, :file_name, :script_file, :hook_config,
                        :setup_instructions, :dependencies, 1, 0)
            ''', default_hooks)

            print(f"✓ Inserted {len(default_hooks)} default hooks")

        conn.commit()
        print("✓ Migration completed successfully!")
        print(f"  - Created default_hooks table")
        print(f"  - Created custom_hooks table")
        print(f"  - Created project_hooks table")
        print(f"  - Created indexes")
        print(f"  - Populated {len(default_hooks)} default hooks")

    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
