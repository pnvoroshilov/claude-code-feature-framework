"""
Migration: Add testing configuration fields to project_settings table
Date: 2025-11-25
Description: Adds test_directory, test_framework, auto_merge_tests, test_staging_dir columns
             for integrated test suite management in AUTO mode.
"""

import sqlite3
import os


def migrate():
    """Add testing configuration columns to project_settings table"""
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "claudetask.db")

    # Ensure database file exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_done = []

        # Add test_directory column
        if 'test_directory' not in columns:
            print("Adding 'test_directory' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN test_directory TEXT DEFAULT 'tests'")
            migrations_done.append('test_directory')
        else:
            print("Column 'test_directory' already exists.")

        # Add test_framework column
        if 'test_framework' not in columns:
            print("Adding 'test_framework' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN test_framework TEXT DEFAULT 'pytest'")
            migrations_done.append('test_framework')
        else:
            print("Column 'test_framework' already exists.")

        # Add auto_merge_tests column
        if 'auto_merge_tests' not in columns:
            print("Adding 'auto_merge_tests' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN auto_merge_tests BOOLEAN DEFAULT 1 NOT NULL")
            migrations_done.append('auto_merge_tests')
        else:
            print("Column 'auto_merge_tests' already exists.")

        # Add test_staging_dir column
        if 'test_staging_dir' not in columns:
            print("Adding 'test_staging_dir' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN test_staging_dir TEXT DEFAULT 'tests/staging'")
            migrations_done.append('test_staging_dir')
        else:
            print("Column 'test_staging_dir' already exists.")

        conn.commit()

        if migrations_done:
            print(f"Migration completed successfully! Added columns: {', '.join(migrations_done)}")
        else:
            print("No migration needed. All columns already exist.")

        return True

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
