#!/usr/bin/env python3
"""
Migration: Add Claude Agent SDK skill to default_skills collection.

This skill provides complete reference for building autonomous agents
using the official Claude Agent SDK (Python).

Run with: python -m migrations.add_claude_agent_sdk_skill
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient


async def migrate():
    """Add Claude Agent SDK skill to MongoDB default_skills collection."""

    # Get MongoDB URI from environment
    mongodb_uri = os.environ.get("MONGODB_CONNECTION_STRING") or os.environ.get("MONGODB_URI")
    if not mongodb_uri:
        print("Error: MONGODB_CONNECTION_STRING or MONGODB_URI environment variable not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongodb_uri)

    try:
        db = client.claudetask
        collection = db.default_skills

        # Check if skill already exists
        existing = await collection.find_one({"name": "Claude Agent SDK"})
        if existing:
            print("Claude Agent SDK skill already exists. Updating...")
            await collection.update_one(
                {"name": "Claude Agent SDK"},
                {"$set": {
                    "description": "Complete reference for Claude Agent SDK (Python) - building autonomous agents with query(), ClaudeSDKClient, MCP servers, hooks, and all built-in tools. Use when building programmatic automation, custom tools, or multi-agent orchestration.",
                    "category": "Development",
                    "file_name": "claude-agent-sdk/skill.md",
                    "is_active": True,
                    "is_favorite": True,
                    "updated_at": datetime.utcnow()
                }}
            )
            print("✓ Updated Claude Agent SDK skill")
            return

        # Insert new skill
        now = datetime.utcnow()
        skill_doc = {
            "name": "Claude Agent SDK",
            "description": "Complete reference for Claude Agent SDK (Python) - building autonomous agents with query(), ClaudeSDKClient, MCP servers, hooks, and all built-in tools. Use when building programmatic automation, custom tools, or multi-agent orchestration.",
            "category": "Development",
            "file_name": "claude-agent-sdk/skill.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        }

        result = await collection.insert_one(skill_doc)
        print(f"✓ Added Claude Agent SDK skill (ID: {result.inserted_id})")

        # Add agent recommendations
        recommendations_collection = db.agent_skill_recommendations

        recommendations = [
            {
                "agent_name": "python-api-expert",
                "skill_name": "Claude Agent SDK",
                "skill_type": "default",
                "priority": 1,
                "reason": "Essential for building Python automation with Claude Agent SDK"
            },
            {
                "agent_name": "backend-architect",
                "skill_name": "Claude Agent SDK",
                "skill_type": "default",
                "priority": 1,
                "reason": "Core skill for designing agent-based backend systems"
            },
            {
                "agent_name": "mcp-engineer",
                "skill_name": "Claude Agent SDK",
                "skill_type": "default",
                "priority": 1,
                "reason": "Critical for MCP server development and integration"
            },
            {
                "agent_name": "devops-engineer",
                "skill_name": "Claude Agent SDK",
                "skill_type": "default",
                "priority": 2,
                "reason": "Useful for CI/CD automation with Claude agents"
            },
            {
                "agent_name": "systems-analyst",
                "skill_name": "Claude Agent SDK",
                "skill_type": "default",
                "priority": 2,
                "reason": "Helpful for designing multi-agent orchestration"
            }
        ]

        for rec in recommendations:
            # Check if recommendation already exists
            existing_rec = await recommendations_collection.find_one({
                "agent_name": rec["agent_name"],
                "skill_name": rec["skill_name"]
            })

            if not existing_rec:
                await recommendations_collection.insert_one(rec)
                print(f"  + Added recommendation: {rec['agent_name']} -> {rec['skill_name']}")

        print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
