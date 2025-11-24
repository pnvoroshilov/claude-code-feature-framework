"""
Migration script to add memory hooks as default hooks
Run this script to add memory system hooks to the default hooks

Updated: Uses command-type hooks (bash scripts) instead of unsupported mcp-type hooks
"""
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

def add_memory_hooks():
    """Add memory hooks to default_hooks table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if memory hooks already exist
        cursor.execute("""
            SELECT COUNT(*) FROM default_hooks
            WHERE file_name IN ('memory-conversation-capture.json', 'memory-session-summarize.json')
        """)

        if cursor.fetchone()[0] > 0:
            print("Memory hooks already exist. Updating...")
            # Delete old versions to replace with new ones
            cursor.execute("""
                DELETE FROM default_hooks
                WHERE file_name IN ('memory-conversation-capture.json', 'memory-session-summarize.json')
            """)

        # Insert memory conversation capture hook (using command type - bash script)
        cursor.execute("""
            INSERT INTO default_hooks (
                name, description, category, file_name, hook_config,
                setup_instructions, dependencies, is_active, is_favorite, script_file
            ) VALUES (
                'Memory Conversation Capture',
                'Automatically captures user and assistant messages to project memory via bash hook',
                'memory',
                'memory-conversation-capture.json',
                :hook_config,
                'This hook captures conversation messages via bash script that calls the backend API. Requires ClaudeTask backend running and project_id configured in .mcp.json.',
                :dependencies,
                1,  -- Active by default
                1,  -- Favorite by default
                'memory-capture.sh'  -- Script file to copy
            )
        """, {
            'hook_config': json.dumps({
                "UserPromptSubmit": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": ".claude/hooks/memory-capture.sh"
                            }
                        ]
                    }
                ],
                "Stop": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": ".claude/hooks/memory-capture.sh"
                            }
                        ]
                    }
                ]
            }),
            'dependencies': json.dumps(["claudetask-backend"])
        })

        # Insert memory session summarizer hook (DEPRECATED - no OnSessionEnd in Claude Code)
        cursor.execute("""
            INSERT INTO default_hooks (
                name, description, category, file_name, hook_config,
                setup_instructions, dependencies, is_active, is_favorite
            ) VALUES (
                'Memory Session Summarizer',
                'DEPRECATED: Claude Code does not support OnSessionEnd. Use manual summary updates via MCP.',
                'memory',
                'memory-session-summarize.json',
                :hook_config,
                'This hook is deprecated. Instead, use the update_project_summary MCP tool directly when you need to save important insights.',
                :dependencies,
                0,  -- NOT active by default (deprecated)
                0   -- Not favorite
            )
        """, {
            'hook_config': json.dumps({}),  # Empty config - deprecated
            'dependencies': json.dumps(["claudetask-mcp"])
        })

        # Enable memory conversation capture hook for all existing projects
        # (but NOT the deprecated session summarizer)
        cursor.execute("""
            INSERT INTO project_hooks (project_id, hook_id, hook_type, enabled_at, enabled_by)
            SELECT p.id, h.id, 'default', datetime('now'), 'migration'
            FROM projects p
            CROSS JOIN default_hooks h
            WHERE h.file_name = 'memory-conversation-capture.json'
            AND NOT EXISTS (
                SELECT 1 FROM project_hooks ph
                WHERE ph.project_id = p.id AND ph.hook_id = h.id
            )
        """)

        conn.commit()
        print("Memory hooks updated successfully!")
        print("  - Memory Conversation Capture (active, uses bash script)")
        print("  - Memory Session Summarizer (deprecated, inactive)")
        print("  - Conversation capture enabled for all existing projects")

    except sqlite3.Error as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    add_memory_hooks()
