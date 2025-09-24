#!/usr/bin/env python
"""
Database migration script to add missing stage_results column
"""
import sqlite3
import json
import sys
from pathlib import Path

def migrate_database():
    """Add stage_results column to tasks table if it doesn't exist"""
    db_path = Path(__file__).parent / "data" / "claudetask.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'stage_results' in column_names:
            print("Column 'stage_results' already exists")
            conn.close()
            return True
        
        # Add the missing column
        print("Adding 'stage_results' column to tasks table...")
        cursor.execute("""
            ALTER TABLE tasks 
            ADD COLUMN stage_results TEXT DEFAULT '[]'
        """)
        
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'stage_results' in column_names:
            print("Verification: Column 'stage_results' has been added successfully")
        else:
            print("ERROR: Column was not added properly")
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