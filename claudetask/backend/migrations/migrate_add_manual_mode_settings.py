"""
Migration: Add manual_testing_mode and manual_review_mode fields to project_settings table
Date: 2025-11-21
Purpose: Support UC-04 (testing variants) and UC-05 (review variants)
"""

import sqlite3
import os

def migrate():
    """Add manual_testing_mode and manual_review_mode columns to project_settings table"""
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "claudetask.db")

    # Ensure database file exists
    if not os.path.exists(db_path):
        print(f"✗ Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(project_settings)")
        columns = [col[1] for col in cursor.fetchall()]

        columns_added = []

        # Add manual_testing_mode if not exists
        if 'manual_testing_mode' not in columns:
            print("Adding 'manual_testing_mode' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN manual_testing_mode BOOLEAN DEFAULT 1 NOT NULL")
            cursor.execute("UPDATE project_settings SET manual_testing_mode = 1 WHERE manual_testing_mode IS NULL")
            columns_added.append('manual_testing_mode')
        else:
            print("✓ Column 'manual_testing_mode' already exists.")

        # Add manual_review_mode if not exists
        if 'manual_review_mode' not in columns:
            print("Adding 'manual_review_mode' column to project_settings table...")
            cursor.execute("ALTER TABLE project_settings ADD COLUMN manual_review_mode BOOLEAN DEFAULT 1 NOT NULL")
            cursor.execute("UPDATE project_settings SET manual_review_mode = 1 WHERE manual_review_mode IS NULL")
            columns_added.append('manual_review_mode')
        else:
            print("✓ Column 'manual_review_mode' already exists.")

        if not columns_added:
            print("✓ No migration needed. All columns already exist.")
            return True

        conn.commit()
        print(f"✓ Migration completed successfully!")
        print(f"✓ Added columns: {', '.join(columns_added)}")
        print(f"✓ All existing project settings set to manual mode (true) by default")
        print("")
        print("ℹ️  Usage:")
        print("  - manual_testing_mode = true: UC-04 Variant B (Manual Testing)")
        print("  - manual_testing_mode = false: UC-04 Variant A (Automated Testing)")
        print("  - manual_review_mode = true: UC-05 Variant B (Manual Review)")
        print("  - manual_review_mode = false: UC-05 Variant A (Auto-merge)")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
