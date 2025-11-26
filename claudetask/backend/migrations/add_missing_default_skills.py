"""
Migration: Add missing default skills to database

This migration adds the following skills that were missing from default_skills:
- Architecture Mindset (Grand Architect's Codex)
- Merge Skill (Git conflict resolution)
- React Refactor (Clean Architecture for React)
- Requirements Analysis
- Technical Design

Run with: python -m migrations.add_missing_default_skills
"""

import sqlite3
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config


def migrate():
    """Add missing default skills to default_skills table"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Skills to add
    new_skills = [
        {
            "name": "Architecture Mindset",
            "description": "The Grand Architect's Codex - a rigorous, trade-off-focused mindset for architectural decisions. Forces abandonment of generic advice in favor of CTO/Principal Architect-level thinking with failure mode analysis, interrogation framework, and systematic trade-off evaluation.",
            "category": "Architecture",
            "file_name": "architecture-mindset/SKILL.md",
            "is_favorite": True,
            "recommendations": [
                ("system-architect", 1, "Essential for rigorous architectural decision-making with trade-off analysis"),
                ("systems-analyst", 1, "Critical for system design with failure mode thinking"),
                ("backend-architect", 1, "Core skill for backend architecture decisions"),
                ("frontend-architect", 2, "Useful for frontend architecture trade-offs"),
                ("devops-architect", 2, "Important for infrastructure architecture decisions"),
            ]
        },
        {
            "name": "Merge Skill",
            "description": "Comprehensive Git branch merging strategies, conflict resolution techniques, and best practices for handling complex merge scenarios including renamed files, binary conflicts, and large-scale refactoring.",
            "category": "Development",
            "file_name": "merge-skill/SKILL.md",
            "is_favorite": False,
            "recommendations": [
                ("pr-merge-agent", 1, "Essential for PR merging and conflict resolution"),
                ("devops-engineer", 2, "Useful for branch management and CI/CD"),
                ("fullstack-code-reviewer", 2, "Helpful for code review and merge decisions"),
            ]
        },
        {
            "name": "React Refactor",
            "description": "Expert React code refactoring using Clean Architecture, component patterns, and modern hooks for transforming legacy class components and prop-drilling into maintainable composable designs with proper state management, TypeScript, and testing.",
            "category": "Quality",
            "file_name": "react-refactor/SKILL.md",
            "is_favorite": True,
            "recommendations": [
                ("refactoring-expert", 1, "Essential for React refactoring with Clean Architecture patterns"),
                ("frontend-developer", 1, "Core skill for React component modernization"),
                ("frontend-architect", 1, "Critical for frontend architecture decisions"),
                ("mobile-react-expert", 1, "Important for React Native refactoring"),
                ("fullstack-code-reviewer", 2, "Useful for reviewing React code quality"),
            ]
        },
        {
            "name": "Requirements Analysis",
            "description": "Comprehensive requirements discovery and analysis framework for transforming user requests into detailed actionable specifications with user stories, acceptance criteria, and stakeholder elicitation.",
            "category": "Analysis",
            "file_name": "requirements-analysis/skill.md",
            "is_favorite": False,
            "recommendations": [
                ("requirements-analyst", 1, "Core skill for requirements gathering"),
                ("business-analyst", 1, "Essential for business requirements analysis"),
                ("systems-analyst", 2, "Helpful for system requirements"),
            ]
        },
        {
            "name": "Technical Design",
            "description": "Comprehensive document formats and templates for technical architecture design, test cases, ADRs (Architecture Decision Records), and conflict analysis.",
            "category": "Documentation",
            "file_name": "technical-design/skill.md",
            "is_favorite": False,
            "recommendations": [
                ("system-architect", 1, "Essential for architecture documentation"),
                ("technical-writer", 1, "Core skill for technical documentation"),
                ("systems-analyst", 2, "Useful for system design documentation"),
                ("backend-architect", 2, "Helpful for backend design docs"),
            ]
        },
    ]

    try:
        added_count = 0
        skipped_count = 0

        for skill in new_skills:
            # Check if skill already exists
            cursor.execute(
                "SELECT id FROM default_skills WHERE name = ?",
                (skill["name"],)
            )
            existing = cursor.fetchone()

            if existing:
                print(f"  SKIP: {skill['name']} already exists")
                skipped_count += 1
                continue

            # Insert the new skill
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO default_skills (
                    name, description, category, file_name, is_active, is_favorite, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill["name"],
                skill["description"],
                skill["category"],
                skill["file_name"],
                1,  # is_active
                1 if skill["is_favorite"] else 0,
                now,
                now
            ))

            skill_id = cursor.lastrowid
            print(f"  ✓ Added: {skill['name']} (ID: {skill_id})")

            # Add agent recommendations
            for agent_name, priority, reason in skill.get("recommendations", []):
                try:
                    cursor.execute("""
                        INSERT INTO agent_skill_recommendations (
                            agent_name, skill_id, skill_type, priority, reason
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        agent_name,
                        skill_id,
                        "default",
                        priority,
                        reason
                    ))
                except sqlite3.IntegrityError:
                    # Recommendation already exists
                    pass

            added_count += 1

        conn.commit()
        print(f"\n=== Migration Complete ===")
        print(f"Added: {added_count} skills")
        print(f"Skipped: {skipped_count} skills (already exist)")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
