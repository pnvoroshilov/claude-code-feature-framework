"""
Migration script to add testing skills:
- unit-testing
- integration-testing
- ui-testing
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config


def migrate():
    """Add unit-testing, integration-testing, and ui-testing skills"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()
    skills_added = 0

    # New testing skills to add
    new_skills = [
        {
            "name": "Unit Testing",
            "description": "Comprehensive unit testing best practices for creating, maintaining, and running unit tests. Covers pytest, Jest, test isolation, mocking strategies, TDD, and improving test coverage across Python, JavaScript, TypeScript and other languages.",
            "category": "Testing",
            "file_name": "unit-testing/SKILL.md",
            "is_favorite": False
        },
        {
            "name": "Integration Testing",
            "description": "Comprehensive integration testing best practices for testing component interactions, APIs, databases, and external services. Covers test environment setup, fixtures, database testing, API testing, and microservices validation.",
            "category": "Testing",
            "file_name": "integration-testing/SKILL.md",
            "is_favorite": False
        },
        {
            "name": "UI Testing",
            "description": "Comprehensive E2E and UI testing best practices covering Playwright, Cypress, Selenium, visual regression, accessibility testing, and Page Object Model patterns. Use for writing E2E tests, setting up test automation, and debugging flaky UI tests.",
            "category": "Testing",
            "file_name": "ui-testing/SKILL.md",
            "is_favorite": False
        },
        {
            "name": "Security Best Practices",
            "description": "Comprehensive security best practices skill covering OWASP Top 10, secure coding patterns, authentication/authorization, input validation, encryption, and security auditing. Use when implementing security measures or reviewing code for vulnerabilities.",
            "category": "Security",
            "file_name": "security-best-practices/SKILL.md",
            "is_favorite": False
        }
    ]

    try:
        for skill in new_skills:
            # Check if skill already exists
            cursor.execute(
                "SELECT id FROM default_skills WHERE name = ?",
                (skill["name"],)
            )
            existing = cursor.fetchone()

            if existing:
                print(f"⚠ Skill '{skill['name']}' already exists (ID: {existing[0]}), skipping")
                continue

            # Insert new skill
            cursor.execute("""
                INSERT INTO default_skills (name, description, category, file_name, is_favorite, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                skill["name"],
                skill["description"],
                skill["category"],
                skill["file_name"],
                skill["is_favorite"],
                now,
                now
            ))

            print(f"✓ Added skill: {skill['name']}")
            print(f"  - Category: {skill['category']}")
            print(f"  - File: {skill['file_name']}")
            skills_added += 1

        conn.commit()
        print(f"\n✓ Migration completed successfully!")
        print(f"  - Skills added: {skills_added}")

        # Add agent recommendations for testing skills
        if skills_added > 0:
            # Get skill IDs
            cursor.execute("SELECT id, name FROM default_skills WHERE name IN ('Unit Testing', 'Integration Testing', 'UI Testing')")
            skill_ids = {row[1]: row[0] for row in cursor.fetchall()}

            recommendations = []

            # web-tester agent recommendations
            if "UI Testing" in skill_ids:
                recommendations.append((
                    "web-tester",
                    skill_ids["UI Testing"],
                    "default",
                    1,
                    "Core skill for E2E and visual regression testing"
                ))

            # quality-engineer agent recommendations
            if "Unit Testing" in skill_ids:
                recommendations.append((
                    "quality-engineer",
                    skill_ids["Unit Testing"],
                    "default",
                    1,
                    "Essential for comprehensive test coverage"
                ))

            if "Integration Testing" in skill_ids:
                recommendations.append((
                    "quality-engineer",
                    skill_ids["Integration Testing"],
                    "default",
                    2,
                    "Important for testing component interactions"
                ))

            # backend-architect agent recommendations
            if "Integration Testing" in skill_ids:
                recommendations.append((
                    "backend-architect",
                    skill_ids["Integration Testing"],
                    "default",
                    2,
                    "Essential for API and database testing"
                ))

            # frontend-developer agent recommendations
            if "Unit Testing" in skill_ids:
                recommendations.append((
                    "frontend-developer",
                    skill_ids["Unit Testing"],
                    "default",
                    2,
                    "Important for React component testing"
                ))

            for rec in recommendations:
                try:
                    cursor.execute("""
                        INSERT INTO agent_skill_recommendations (agent_name, skill_id, skill_type, priority, reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (*rec, now))
                    print(f"  ✓ Added recommendation: {rec[0]} -> skill ID {rec[1]}")
                except sqlite3.IntegrityError:
                    print(f"  ⚠ Recommendation already exists: {rec[0]} -> skill ID {rec[1]}")

            conn.commit()
            print(f"\n✓ Agent recommendations added: {len(recommendations)}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
