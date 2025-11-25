"""
Migration script to add Merge Skill default skill
Run this script to add the new skill to the database
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config


def migrate():
    """Add Merge Skill to default_skills table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if skill already exists
        cursor.execute(
            "SELECT id FROM default_skills WHERE name = 'Merge Skill'"
        )
        existing = cursor.fetchone()

        if existing:
            print("✓ Merge Skill already exists. No migration needed.")
            return

        # Insert the new skill
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO default_skills (
                name, description, category, file_name, is_active, is_favorite, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Merge Skill",
            "Comprehensive Git branch merging strategies, conflict resolution techniques, and best practices for handling complex merge scenarios including renamed files, binary conflicts, and large-scale refactoring",
            "Git",
            "merge-skill/SKILL.md",
            1,  # is_active
            1,  # is_favorite
            now,
            now
        ))

        skill_id = cursor.lastrowid
        print(f"✓ Added Merge Skill (ID: {skill_id})")

        # Add agent recommendations
        recommendations = [
            ("git-workflow-expert", 1, "Essential for advanced merge strategies and conflict resolution"),
            ("fullstack-code-reviewer", 2, "Useful for reviewing merge resolutions and ensuring code quality"),
            ("devops-expert", 2, "Important for CI/CD integration and automated merge checks"),
            ("tech-lead", 2, "Critical for establishing team merge conventions and best practices"),
            ("refactoring-expert", 2, "Helpful for handling large-scale refactoring merge conflicts"),
        ]

        for agent_name, priority, reason in recommendations:
            cursor.execute("""
                INSERT INTO agent_skill_recommendations (
                    agent_name, skill_id, skill_type, priority, reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agent_name,
                skill_id,
                "default",
                priority,
                reason,
                now
            ))
            print(f"  ✓ Added recommendation for {agent_name}")

        conn.commit()
        print(f"\n✓ Migration completed successfully!")
        print(f"  - Skill added: Merge Skill (ID: {skill_id})")
        print(f"  - Recommendations added: {len(recommendations)}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
