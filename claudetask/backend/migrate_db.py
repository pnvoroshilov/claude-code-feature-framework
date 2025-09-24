#!/usr/bin/env python
"""
Database migration script to add missing columns
"""
import sqlite3
import json
import sys
from pathlib import Path

def migrate_database():
    """Add missing columns to tasks table if they don't exist"""
    db_path = Path(__file__).parent / "data" / "claudetask.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        columns_added = []
        
        # Check and add stage_results column
        if 'stage_results' not in column_names:
            print("Adding 'stage_results' column to tasks table...")
            cursor.execute("""
                ALTER TABLE tasks 
                ADD COLUMN stage_results TEXT DEFAULT '[]'
            """)
            columns_added.append('stage_results')
        else:
            print("Column 'stage_results' already exists")
        
        # Check and add testing_urls column
        if 'testing_urls' not in column_names:
            print("Adding 'testing_urls' column to tasks table...")
            cursor.execute("""
                ALTER TABLE tasks 
                ADD COLUMN testing_urls TEXT DEFAULT NULL
            """)
            columns_added.append('testing_urls')
        else:
            print("Column 'testing_urls' already exists")
        
        if not columns_added:
            print("All columns already exist")
            conn.close()
            return True
        
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the columns were added
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        for col in columns_added:
            if col in column_names:
                print(f"Verification: Column '{col}' has been added successfully")
            else:
                print(f"ERROR: Column '{col}' was not added properly")
                conn.close()
                return False
            
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)