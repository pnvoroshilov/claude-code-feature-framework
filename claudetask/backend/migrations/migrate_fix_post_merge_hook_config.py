"""
Fix Post-Merge Documentation hook_config to use script reference
This migration updates the hook_config JSON in default_hooks table
"""
import sqlite3
import sys
import json
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def fix_hook_config():
    """Update Post-Merge Documentation hook_config to use script reference"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Correct hook_config with script reference
        correct_hook_config = {
            "PostToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": ".claude/hooks/post-push-docs.sh"
                        }
                    ]
                }
            ]
        }

        # Update the Post-Merge Documentation Update hook
        cursor.execute("""
            UPDATE default_hooks
            SET hook_config = ?
            WHERE name = 'Post-Merge Documentation Update'
        """, (json.dumps(correct_hook_config),))

        if cursor.rowcount > 0:
            print(f"✓ Updated {cursor.rowcount} hook(s)")
            conn.commit()
            print("✓ Post-Merge Documentation Update hook_config fixed:")
            print(f"  - Now uses: .claude/hooks/post-push-docs.sh")
            print(f"  - Instead of: inline bash command")
        else:
            print("⚠ No hook found with name 'Post-Merge Documentation Update'")

    except sqlite3.Error as e:
        print(f"✗ Update failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    fix_hook_config()
