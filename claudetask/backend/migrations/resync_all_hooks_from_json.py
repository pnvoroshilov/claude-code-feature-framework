"""
Re-sync ALL default hooks from framework-assets JSON files to database
This script reads all hook JSON files and updates the hook_config in default_hooks table
Use this whenever hook JSON files are updated to refresh the database
"""
import sqlite3
import sys
import json
import os
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def resync_hooks():
    """Re-sync all default hooks from JSON files to database"""
    config = get_config()
    db_path = config.sqlite_db_path

    # Get framework hooks directory
    script_dir = Path(__file__).parent
    framework_root = script_dir.parent.parent.parent
    hooks_dir = framework_root / "framework-assets" / "claude-hooks"

    if not hooks_dir.exists():
        print(f"✗ Framework hooks directory not found: {hooks_dir}")
        return

    print(f"Connecting to database: {db_path}")
    print(f"Reading hooks from: {hooks_dir}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    updated_count = 0
    error_count = 0

    try:
        # Get all JSON files from framework-assets/claude-hooks/
        for hook_file in hooks_dir.glob("*.json"):
            try:
                # Read hook JSON
                with open(hook_file, 'r', encoding='utf-8') as f:
                    hook_data = json.load(f)

                hook_name = hook_data.get('name')
                hook_config = hook_data.get('hook_config', {})
                script_file = hook_data.get('script_file')
                description = hook_data.get('description', '')
                setup_instructions = hook_data.get('setup_instructions', '')
                dependencies = hook_data.get('dependencies', [])

                if not hook_name:
                    print(f"⚠ Skipping {hook_file.name}: No 'name' field")
                    continue

                # Update hook in database
                cursor.execute("""
                    UPDATE default_hooks
                    SET
                        hook_config = ?,
                        script_file = ?,
                        description = ?,
                        setup_instructions = ?,
                        dependencies = ?
                    WHERE name = ?
                """, (
                    json.dumps(hook_config),
                    script_file,
                    description,
                    setup_instructions,
                    json.dumps(dependencies),
                    hook_name
                ))

                if cursor.rowcount > 0:
                    print(f"✓ Updated: {hook_name}")
                    if script_file:
                        print(f"  - script_file: {script_file}")
                    updated_count += 1
                else:
                    print(f"⚠ Not found in DB: {hook_name}")

            except Exception as e:
                print(f"✗ Error processing {hook_file.name}: {e}")
                error_count += 1

        conn.commit()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  - Updated: {updated_count} hook(s)")
        print(f"  - Errors: {error_count}")
        print(f"{'='*60}")

        if updated_count > 0:
            print("\n✓ Database successfully synced with JSON files")
            print("\n⚠ NOTE: Projects with enabled hooks may need to:")
            print("  1. Disable the hook in UI")
            print("  2. Re-enable it to apply the new configuration")

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    resync_hooks()
