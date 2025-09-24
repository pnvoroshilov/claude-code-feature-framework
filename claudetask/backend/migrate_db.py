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
        
        columns_added = False
        
        # Add stage_results column if missing
        if 'stage_results' not in column_names:
            print("Adding 'stage_results' column to tasks table...")
            cursor.execute("""
                ALTER TABLE tasks 
                ADD COLUMN stage_results TEXT DEFAULT '[]'
            """)
            columns_added = True
            print("Column 'stage_results' added successfully")
        else:
            print("Column 'stage_results' already exists")
        
        # Add testing_urls column if missing
        if 'testing_urls' not in column_names:
            print("Adding 'testing_urls' column to tasks table...")
            cursor.execute("""
                ALTER TABLE tasks 
                ADD COLUMN testing_urls TEXT DEFAULT NULL
            """)
            columns_added = True
            print("Column 'testing_urls' added successfully")
        else:
            print("Column 'testing_urls' already exists")
        
        if columns_added:
            conn.commit()
            print("Migration completed successfully!")
            
            # Verify the columns were added
            cursor.execute("PRAGMA table_info(tasks)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'stage_results' in column_names and 'testing_urls' in column_names:
                print("Verification: All columns have been added successfully")
            else:
                print("ERROR: Some columns were not added properly")
                conn.close()
                return False
        else:
            print("No migrations needed - all columns already exist")
            
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