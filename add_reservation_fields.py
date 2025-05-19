import sqlite3
import os

def add_reservation_fields():
    """Add objetivos and requiere_pasajes fields to the reservations table"""
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
        cursor.execute("PRAGMA table_info(reservations)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Add objetivos column if it doesn't exist
        if 'objetivos' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN objetivos TEXT")
            print("Added 'objetivos' column to reservations table")
        else:
            print("Column 'objetivos' already exists")
        
        # Add requiere_pasajes column if it doesn't exist
        if 'requiere_pasajes' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN requiere_pasajes BOOLEAN DEFAULT 0")
            print("Added 'requiere_pasajes' column to reservations table")
        else:
            print("Column 'requiere_pasajes' already exists")
        
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
    add_reservation_fields()
