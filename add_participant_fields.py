import sqlite3
import os

def add_participant_fields():
    """Add CUIL and birth_date fields to the participants table"""
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
        
        # Add cuil column if it doesn't exist
        if 'cuil' not in columns:
            cursor.execute("ALTER TABLE participants ADD COLUMN cuil VARCHAR(20)")
            print("Added 'cuil' column to participants table")
        else:
            print("Column 'cuil' already exists")
        
        # Add birth_date column if it doesn't exist
        if 'birth_date' not in columns:
            cursor.execute("ALTER TABLE participants ADD COLUMN birth_date DATE")
            print("Added 'birth_date' column to participants table")
        else:
            print("Column 'birth_date' already exists")
        
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
    add_participant_fields()
