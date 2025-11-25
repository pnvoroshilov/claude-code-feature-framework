"""
Migration script to add Python Refactor default skill
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
    """Add Python Refactor skill to default_skills table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if skill already exists
        cursor.execute(
            "SELECT id FROM default_skills WHERE name = 'Python Refactor'"
        )
        existing = cursor.fetchone()

        if existing:
            print("✓ Python Refactor skill already exists. No migration needed.")
            return

        # Insert the new skill
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO default_skills (
                name, description, category, file_name, is_active, is_favorite, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Python Refactor",
            "Expert Python code refactoring using Clean Architecture, DDD, and SOLID principles for transforming legacy systems into maintainable domain-driven designs",
            "Quality",
            "python-refactor/SKILL.md",
            1,  # is_active
            1,  # is_favorite
            now,
            now
        ))

        skill_id = cursor.lastrowid
        print(f"✓ Added Python Refactor skill (ID: {skill_id})")

        # Add agent recommendations
        recommendations = [
            ("refactoring-expert", 1, "Essential for Python refactoring with Clean Architecture and DDD patterns"),
            ("backend-architect", 1, "Critical for designing clean Python backend architecture"),
            ("python-api-expert", 1, "Important for structuring FastAPI applications with Clean Architecture"),
            ("python-expert", 1, "Core skill for Python code quality and architectural patterns"),
            ("fullstack-code-reviewer", 2, "Useful for reviewing Python code against Clean Architecture principles"),
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
        print(f"  - Skill added: Python Refactor (ID: {skill_id})")
        print(f"  - Recommendations added: {len(recommendations)}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
