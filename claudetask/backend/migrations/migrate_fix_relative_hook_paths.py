#!/usr/bin/env python3
"""
Migration: Fix relative hook paths in settings.json

This migration converts relative paths (.claude/hooks/...) to absolute paths
in all project settings.json files. This is required for worktree support.

When Claude Code runs from a worktree directory, relative paths don't work
because the worktree is in a different location than the main project.

Run with: python -m claudetask.backend.migrations.migrate_fix_relative_hook_paths
"""

import os
import sys
import json
import sqlite3
from pathlib import Path


def get_db_path():
    """Get database path from config or default"""
    # Try to import from config
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
        from claudetask.config import CLAUDETASK_DB_PATH
        return CLAUDETASK_DB_PATH
    except ImportError:
        pass

    # Fallback locations to check
    locations = [
        os.path.join(os.path.expanduser("~"), ".claude", "claudetask.db"),
        os.path.join(os.path.expanduser("~"), ".claudetask", "claudetask.db"),
        os.path.join(Path(__file__).parent.parent, "data", "claudetask.db"),
        os.path.join(Path(__file__).parent.parent, "claudetask.db"),
    ]

    for loc in locations:
        if os.path.exists(loc):
            return loc

    # Return first location as default
    return locations[0]


def convert_relative_to_absolute(command: str, project_path: str) -> str:
    """Convert relative .claude/hooks/ path to absolute path with proper quoting"""
    result = command

    if command.startswith(".claude/hooks/"):
        result = os.path.join(project_path, command)

    # Wrap in quotes if path contains spaces (for shell compatibility)
    if result.startswith("/") and ' ' in result and not result.startswith('"'):
        result = f'"{result}"'

    return result


def fix_settings_json(project_path: str) -> tuple[bool, str]:
    """
    Fix relative paths in project's settings.json

    Returns:
        (changed, message) tuple
    """
    settings_path = os.path.join(project_path, ".claude", "settings.json")

    if not os.path.exists(settings_path):
        return False, f"No settings.json found at {settings_path}"

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return False, "Empty settings.json"
            settings = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in settings.json: {e}"
    except Exception as e:
        return False, f"Error reading settings.json: {e}"

    if "hooks" not in settings:
        return False, "No hooks section in settings.json"

    changed = False
    changes = []

    for event_type, event_hooks in settings["hooks"].items():
        if not isinstance(event_hooks, list):
            continue

        for hook_matcher in event_hooks:
            if not isinstance(hook_matcher, dict):
                continue

            hooks_list = hook_matcher.get("hooks", [])
            if not isinstance(hooks_list, list):
                continue

            for hook in hooks_list:
                if not isinstance(hook, dict):
                    continue

                command = hook.get("command", "")
                if command.startswith(".claude/hooks/"):
                    old_command = command
                    new_command = convert_relative_to_absolute(command, project_path)
                    hook["command"] = new_command
                    changed = True
                    changes.append(f"  {old_command} -> {new_command}")

    if changed:
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(settings, indent=2))
            return True, f"Fixed {len(changes)} path(s):\n" + "\n".join(changes)
        except Exception as e:
            return False, f"Error writing settings.json: {e}"

    return False, "No relative paths found to fix"


def main():
    print("=" * 60)
    print("Migration: Fix Relative Hook Paths")
    print("=" * 60)
    print()
    print("This migration converts relative paths (.claude/hooks/...)")
    print("to absolute paths in all project settings.json files.")
    print()

    db_path = get_db_path()
    print(f"Database: {db_path}")

    if not os.path.exists(db_path):
        print("ERROR: Database not found")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all projects
    cursor.execute("SELECT id, name, path FROM projects")
    projects = cursor.fetchall()

    if not projects:
        print("No projects found in database")
        conn.close()
        sys.exit(0)

    print(f"\nFound {len(projects)} project(s)")
    print("-" * 60)

    fixed_count = 0
    error_count = 0
    skipped_count = 0

    for project_id, name, path in projects:
        print(f"\nProject: {name}")
        print(f"  Path: {path}")

        if not os.path.exists(path):
            print(f"  SKIPPED: Project path does not exist")
            skipped_count += 1
            continue

        changed, message = fix_settings_json(path)

        if changed:
            print(f"  FIXED: {message}")
            fixed_count += 1
        else:
            print(f"  OK: {message}")

    conn.close()

    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Fixed:   {fixed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors:  {error_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
