"""
Migration script to add memory hooks as default hooks
Run this script to add memory system hooks to the default hooks
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
            print("✓ Memory hooks already exist. Updating...")
            # Delete old versions to replace with new ones
            cursor.execute("""
                DELETE FROM default_hooks
                WHERE file_name IN ('memory-conversation-capture.json', 'memory-session-summarize.json')
            """)

        # Insert memory conversation capture hook
        cursor.execute("""
            INSERT INTO default_hooks (
                name, description, category, file_name, hook_config,
                setup_instructions, dependencies, is_active, is_favorite
            ) VALUES (
                'Memory Conversation Capture',
                'Automatically captures all conversation messages to project memory for context persistence',
                'memory',
                'memory-conversation-capture.json',
                :hook_config,
                'This hook automatically captures all conversation messages to the project memory database. It also loads the project context at session start. Requires the ClaudeTask MCP server to be running.',
                :dependencies,
                1,  -- Active by default
                1   -- Favorite by default
            )
        """, {
            'hook_config': json.dumps({
                "PostToolUse": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "mcp",
                                "tool": "save_conversation_message",
                                "params": {
                                    "message_type": "assistant",
                                    "content": "$TOOL_OUTPUT"
                                }
                            }
                        ]
                    }
                ],
                "PreUserPromptSubmit": [
                    {
                        "hooks": [
                            {
                                "type": "mcp",
                                "tool": "save_conversation_message",
                                "params": {
                                    "message_type": "user",
                                    "content": "$USER_INPUT"
                                }
                            }
                        ]
                    }
                ],
                "OnSessionStart": [
                    {
                        "hooks": [
                            {
                                "type": "mcp",
                                "tool": "get_project_memory_context",
                                "params": {}
                            }
                        ]
                    }
                ]
            }),
            'dependencies': json.dumps(["claudetask-mcp"])
        })

        # Insert memory session summarizer hook
        cursor.execute("""
            INSERT INTO default_hooks (
                name, description, category, file_name, hook_config,
                setup_instructions, dependencies, is_active, is_favorite
            ) VALUES (
                'Memory Session Summarizer',
                'Automatically summarizes session insights and updates project memory on session end or important events',
                'memory',
                'memory-session-summarize.json',
                :hook_config,
                'This hook automatically triggers project summary updates at key moments: session end and when important architectural decisions are made. Works with the ClaudeTask memory system.',
                :dependencies,
                1,  -- Active by default
                0   -- Not favorite (optional)
            )
        """, {
            'hook_config': json.dumps({
                "OnSessionEnd": [
                    {
                        "hooks": [
                            {
                                "type": "mcp",
                                "tool": "update_project_summary",
                                "params": {
                                    "trigger": "session_end",
                                    "new_insights": "Session completed. Key activities: $SESSION_SUMMARY"
                                }
                            }
                        ]
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Edit|Write",
                        "condition": "contains(TOOL_OUTPUT, 'architecture') || contains(TOOL_OUTPUT, 'critical') || contains(TOOL_OUTPUT, 'important')",
                        "hooks": [
                            {
                                "type": "mcp",
                                "tool": "update_project_summary",
                                "params": {
                                    "trigger": "important_decision",
                                    "new_insights": "Important change made: $TOOL_DESCRIPTION"
                                }
                            }
                        ]
                    }
                ]
            }),
            'dependencies': json.dumps(["claudetask-mcp"])
        })

        # Enable memory hooks for all existing projects
        cursor.execute("""
            INSERT INTO project_hooks (project_id, hook_id, hook_type, enabled_at, enabled_by)
            SELECT p.id, h.id, 'default', datetime('now'), 'migration'
            FROM projects p
            CROSS JOIN default_hooks h
            WHERE h.file_name IN ('memory-conversation-capture.json', 'memory-session-summarize.json')
            AND NOT EXISTS (
                SELECT 1 FROM project_hooks ph
                WHERE ph.project_id = p.id AND ph.hook_id = h.id
            )
        """)

        conn.commit()
        print("✓ Memory hooks added successfully!")
        print("  - Memory Conversation Capture (active, favorite)")
        print("  - Memory Session Summarizer (active)")
        print("  - Enabled for all existing projects")

    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    add_memory_hooks()