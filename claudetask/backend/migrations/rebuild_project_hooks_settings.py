"""
Rebuild .claude/settings.json for a project from enabled hooks in database
This script re-applies all enabled hooks to settings.json using the current hook_config from database
Use this to fix projects that have outdated hook configurations in settings.json
"""
import sqlite3
import sys
import json
import os
import asyncio
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

async def rebuild_project_settings(project_id: str):
    """Rebuild settings.json for a project from database"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get project details
        cursor.execute("SELECT id, name, path FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()

        if not project:
            print(f"✗ Project {project_id} not found")
            return

        project_id, project_name, project_path = project
        print(f"Project: {project_name}")
        print(f"Path: {project_path}")

        # Get all enabled hooks for this project
        cursor.execute("""
            SELECT ph.hook_id, ph.hook_type
            FROM project_hooks ph
            WHERE ph.project_id = ?
        """, (project_id,))

        enabled_hooks = cursor.fetchall()
        print(f"Enabled hooks: {len(enabled_hooks)}")

        if not enabled_hooks:
            print("⚠ No enabled hooks found for this project")
            return

        # Build merged hooks configuration
        merged_hooks_config = {}

        for hook_id, hook_type in enabled_hooks:
            # Get hook details
            if hook_type == "default":
                cursor.execute("""
                    SELECT name, hook_config
                    FROM default_hooks
                    WHERE id = ?
                """, (hook_id,))
            else:
                cursor.execute("""
                    SELECT name, hook_config
                    FROM custom_hooks
                    WHERE id = ?
                """, (hook_id,))

            hook_data = cursor.fetchone()

            if not hook_data:
                print(f"⚠ Hook {hook_id} ({hook_type}) not found in database")
                continue

            hook_name, hook_config_json = hook_data
            print(f"  - Processing: {hook_name} ({hook_type})")

            try:
                hook_config = json.loads(hook_config_json)
            except json.JSONDecodeError as e:
                print(f"    ✗ Invalid JSON in hook_config: {e}")
                continue

            # Merge hook config into merged_hooks_config
            for event_type, event_hooks in hook_config.items():
                if event_type not in merged_hooks_config:
                    merged_hooks_config[event_type] = []

                # Add all matchers from this hook
                for matcher_config in event_hooks:
                    # Avoid duplicates by checking matcher name
                    existing_matchers = [m.get("matcher") for m in merged_hooks_config[event_type]]
                    if matcher_config.get("matcher") not in existing_matchers:
                        merged_hooks_config[event_type].append(matcher_config)
                        print(f"    ✓ Added: {event_type} / {matcher_config.get('matcher')}")

        # Write to .claude/settings.json
        settings_path = os.path.join(project_path, ".claude", "settings.json")

        # Read existing settings
        settings = {}
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    settings = json.loads(content)

        # Replace hooks section
        settings["hooks"] = merged_hooks_config

        # Write back to file
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(settings, indent=2))

        print(f"\n✓ Successfully rebuilt {settings_path}")
        print(f"  - Event types: {list(merged_hooks_config.keys())}")
        print(f"  - Total matchers: {sum(len(v) for v in merged_hooks_config.values())}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python rebuild_project_hooks_settings.py <project_id>")
        print("\nExample: python rebuild_project_hooks_settings.py 550e8400-e29b-41d4-a716-446655440000")
        sys.exit(1)

    project_id = sys.argv[1]
    asyncio.run(rebuild_project_settings(project_id))

if __name__ == "__main__":
    main()
