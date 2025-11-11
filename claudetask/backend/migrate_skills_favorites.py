#!/usr/bin/env python
"""
Database migration script to add is_favorite column to Skills tables
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add is_favorite column to default_skills and custom_skills tables"""
    db_path = Path(__file__).parent / "data" / "claudetask.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("Starting Skills favorites migration...")

        # Check and add is_favorite to default_skills
        cursor.execute("PRAGMA table_info(default_skills)")
        default_columns = {col[1] for col in cursor.fetchall()}

        if 'is_favorite' not in default_columns:
            print("Adding 'is_favorite' column to default_skills table...")
            cursor.execute("""
                ALTER TABLE default_skills
                ADD COLUMN is_favorite BOOLEAN DEFAULT 0
            """)
            print("✓ Added is_favorite to default_skills")
        else:
            print("Column 'is_favorite' already exists in default_skills")

        # Check and add is_favorite to custom_skills
        cursor.execute("PRAGMA table_info(custom_skills)")
        custom_columns = {col[1] for col in cursor.fetchall()}

        if 'is_favorite' not in custom_columns:
            print("Adding 'is_favorite' column to custom_skills table...")
            cursor.execute("""
                ALTER TABLE custom_skills
                ADD COLUMN is_favorite BOOLEAN DEFAULT 0
            """)
            print("✓ Added is_favorite to custom_skills")
        else:
            print("Column 'is_favorite' already exists in custom_skills")

        conn.commit()
        print("\nMigration completed successfully!")

        # Verify the columns were added
        cursor.execute("PRAGMA table_info(default_skills)")
        default_columns_after = {col[1] for col in cursor.fetchall()}
        cursor.execute("PRAGMA table_info(custom_skills)")
        custom_columns_after = {col[1] for col in cursor.fetchall()}

        if 'is_favorite' in default_columns_after and 'is_favorite' in custom_columns_after:
            print("✓ Verification passed: is_favorite column exists in both tables")
        else:
            print("ERROR: Verification failed")
            return False

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Skills Favorites Migration: Adding is_favorite column")
    print("=" * 60)
    success = migrate_database()
    sys.exit(0 if success else 1)
