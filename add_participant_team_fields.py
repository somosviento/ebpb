import sqlite3
import os

def add_participant_fields_for_team():
    """Add cargo and nacionalidad fields to the participants table"""
    # Path to the database file
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ebpb.db')
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(participants)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Add cargo column if it doesn't exist
        if 'cargo' not in columns:
            cursor.execute("ALTER TABLE participants ADD COLUMN cargo VARCHAR(100)")
            print("Added 'cargo' column to participants table")
        else:
            print("Column 'cargo' already exists")
        
        # Add nacionalidad column if it doesn't exist
        if 'nacionalidad' not in columns:
            cursor.execute("ALTER TABLE participants ADD COLUMN nacionalidad VARCHAR(100)")
            print("Added 'nacionalidad' column to participants table")
        else:
            print("Column 'nacionalidad' already exists")
        
        # Commit changes
        conn.commit()
        print("Database update completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating database: {str(e)}")
    
    finally:
        # Close connection
        conn.close()

if __name__ == "__main__":
    add_participant_fields_for_team()
