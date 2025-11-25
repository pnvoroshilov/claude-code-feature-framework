"""
Migration script to update Refactoring and Architecture Patterns skills
- Fix file_name paths (skill.md -> SKILL.md)
- Update descriptions to include new content (scalability, infrastructure patterns, decision frameworks)
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config


def migrate():
    """Update Refactoring and Architecture Patterns skills"""
    config = get_config()
    db_path = config.sqlite_db_path

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()
    updates_made = 0

    try:
        # Update Refactoring skill
        cursor.execute(
            "SELECT id, file_name, description FROM default_skills WHERE name = 'Refactoring'"
        )
        refactoring = cursor.fetchone()

        if refactoring:
            skill_id, current_file, current_desc = refactoring
            new_file = "refactoring/SKILL.md"
            new_desc = (
                "Expert code refactoring and cleanup for maintainability, performance, and code quality improvement. "
                "Includes scalability patterns (caching, pagination, high load, high availability), "
                "performance optimization, and practical decision frameworks for when to apply each pattern."
            )

            cursor.execute("""
                UPDATE default_skills
                SET file_name = ?, description = ?, updated_at = ?
                WHERE id = ?
            """, (new_file, new_desc, now, skill_id))

            print(f"✓ Updated Refactoring skill (ID: {skill_id})")
            print(f"  - file_name: {current_file} -> {new_file}")
            print(f"  - description updated with scalability patterns")
            updates_made += 1
        else:
            print("⚠ Refactoring skill not found in database")

        # Update Architecture Patterns skill
        cursor.execute(
            "SELECT id, description FROM default_skills WHERE name = 'Architecture Patterns'"
        )
        architecture = cursor.fetchone()

        if architecture:
            skill_id, current_desc = architecture
            new_desc = (
                "Comprehensive guide to software architecture patterns including SOLID principles, Clean Architecture, "
                "DDD, design patterns, and anti-patterns. Now includes infrastructure patterns "
                "(microservices, Docker, Kubernetes, high availability), and decision frameworks "
                "for choosing between caching, pagination, scaling, and architectural approaches."
            )

            cursor.execute("""
                UPDATE default_skills
                SET description = ?, updated_at = ?
                WHERE id = ?
            """, (new_desc, now, skill_id))

            print(f"✓ Updated Architecture Patterns skill (ID: {skill_id})")
            print(f"  - description updated with infrastructure patterns and decision frameworks")
            updates_made += 1
        else:
            print("⚠ Architecture Patterns skill not found in database")

        conn.commit()
        print(f"\n✓ Migration completed successfully!")
        print(f"  - Skills updated: {updates_made}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
