#!/usr/bin/env python3
"""
Test script for Claude Code sessions reader
Demonstrates reading and parsing Claude Code session data
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "claudetask" / "backend"))

from app.services.claude_sessions_reader import ClaudeSessionsReader


def main():
    """Test Claude sessions reader"""
    reader = ClaudeSessionsReader()

    print("=" * 80)
    print("🔍 CLAUDE CODE SESSIONS READER TEST")
    print("=" * 80)
    print()

    # 1. Get all projects
    print("📁 ALL CLAUDE CODE PROJECTS:")
    print("-" * 80)
    projects = reader.get_all_projects()

    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']}")
        print(f"   Path: {project['path']}")
        print(f"   Sessions: {project['sessions_count']}")
        print(f"   Last Modified: {project['last_modified']}")
        print()

    if not projects:
        print("No Claude Code projects found in ~/.claude/projects/")
        return

    # 2. Get sessions for first project
    project = projects[0]
    print(f"\n📋 SESSIONS FOR PROJECT: {project['name']}")
    print("-" * 80)

    sessions = reader.get_project_sessions(project['name'])

    for i, session in enumerate(sessions[:5], 1):  # Show first 5 sessions
        print(f"{i}. Session ID: {session['session_id'][:12]}...")
        print(f"   Working Dir: {session['cwd']}")
        print(f"   Branch: {session['git_branch']}")
        print(f"   Messages: {session['message_count']} (User: {session['user_messages']}, Assistant: {session['assistant_messages']})")
        print(f"   Created: {session['created_at']}")
        print(f"   File Size: {session['file_size'] / 1024:.1f} KB")

        if session['tool_calls']:
            print(f"   Top Tools: {', '.join(list(session['tool_calls'].keys())[:3])}")

        if session['files_modified']:
            print(f"   Files Modified: {len(session['files_modified'])}")

        if session['errors']:
            print(f"   ⚠️ Errors: {len(session['errors'])}")

        print()

    # 3. Get detailed session info
    if sessions:
        print(f"\n🔎 DETAILED SESSION INFO:")
        print("-" * 80)

        session_id = sessions[0]['session_id']
        detailed = reader.get_session_details(
            project_name=project['name'],
            session_id=session_id,
            include_messages=True
        )

        if detailed:
            print(f"Session: {session_id[:12]}...")
            print(f"Commands Used: {', '.join(detailed['commands_used']) if detailed['commands_used'] else 'None'}")
            print(f"\nTool Usage:")
            for tool, count in list(detailed['tool_calls'].items())[:5]:
                print(f"  - {tool}: {count} times")

            if detailed.get('messages'):
                print(f"\nRecent Messages: ({len(detailed['messages'])} total)")
                for msg in detailed['messages'][-3:]:  # Last 3 messages
                    print(f"  [{msg['type']}] {msg['content'][:100]}...")

    # 4. Get statistics
    print(f"\n📊 OVERALL STATISTICS:")
    print("-" * 80)

    stats = reader.get_session_statistics(project_name=project['name'])

    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Total Files Modified: {stats['total_files_modified']}")
    print(f"Total Errors: {stats['total_errors']}")

    print(f"\nMost Used Tools:")
    sorted_tools = sorted(stats['total_tool_calls'].items(), key=lambda x: x[1], reverse=True)
    for tool, count in sorted_tools[:10]:
        print(f"  - {tool}: {count} times")

    # 5. Search example
    print(f"\n🔍 SEARCH EXAMPLE (searching for 'error'):")
    print("-" * 80)

    search_results = reader.search_sessions(query="error", project_name=project['name'])
    print(f"Found {len(search_results)} sessions containing 'error'")

    for i, result in enumerate(search_results[:3], 1):
        print(f"{i}. Session {result['session_id'][:12]}... - {result['message_count']} messages")


if __name__ == "__main__":
    main()
