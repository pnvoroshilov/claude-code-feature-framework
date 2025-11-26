"""
Migration script to add Architecture Mindset default skill (The Grand Architect's Codex)
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
    """Add Architecture Mindset skill to default_skills table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if skill already exists
        cursor.execute(
            "SELECT id FROM default_skills WHERE name = 'Architecture Mindset'"
        )
        existing = cursor.fetchone()

        if existing:
            print("Architecture Mindset skill already exists. No migration needed.")
            return

        # Insert the new skill
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO default_skills (
                name, description, category, file_name, is_active, is_favorite, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Architecture Mindset",
            "The Grand Architect's Codex - a rigorous, trade-off-focused mindset for architectural decisions. Forces abandonment of generic advice in favor of CTO/Principal Architect-level thinking with failure mode analysis, interrogation framework, and systematic trade-off evaluation.",
            "Architecture",
            "architecture-mindset/SKILL.md",
            1,  # is_active
            1,  # is_favorite (mark as favorite for visibility)
            now,
            now
        ))

        skill_id = cursor.lastrowid
        print(f"Added Architecture Mindset skill (ID: {skill_id})")

        # Add agent recommendations - which agents benefit from this skill
        recommendations = [
            ("system-architect", 1, "Essential for rigorous architectural decision-making with trade-off analysis"),
            ("systems-analyst", 1, "Critical for system design with failure mode thinking"),
            ("backend-architect", 1, "Core skill for backend architecture decisions"),
            ("frontend-architect", 2, "Useful for frontend architecture trade-offs"),
            ("devops-architect", 2, "Important for infrastructure architecture decisions"),
            ("tech-lead", 1, "Essential for technical leadership and architectural guidance"),
            ("requirements-analyst", 2, "Helpful for understanding technical constraints"),
            ("fullstack-code-reviewer", 2, "Useful for reviewing architectural decisions"),
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
            print(f"  Added recommendation for {agent_name}")

        conn.commit()
        print(f"\nMigration completed successfully!")
        print(f"  - Skill added: Architecture Mindset (ID: {skill_id})")
        print(f"  - Recommendations added: {len(recommendations)}")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
