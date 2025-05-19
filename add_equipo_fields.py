import sqlite3
import os

def add_equipo_fields():
    """Add additional fields for equipo de investigación to the reservations table"""
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
        
        # Add activity_sites column if it doesn't exist
        if 'activity_sites' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN activity_sites VARCHAR(255)")
            print("Added 'activity_sites' column to reservations table")
        else:
            print("Column 'activity_sites' already exists")
        
        # Add requiere_ayudantes column if it doesn't exist
        if 'requiere_ayudantes' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN requiere_ayudantes BOOLEAN DEFAULT 0")
            print("Added 'requiere_ayudantes' column to reservations table")
        else:
            print("Column 'requiere_ayudantes' already exists")
        
        # Add requiere_pasajes_equipo column if it doesn't exist
        if 'requiere_pasajes_equipo' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN requiere_pasajes_equipo BOOLEAN DEFAULT 0")
            print("Added 'requiere_pasajes_equipo' column to reservations table")
        else:
            print("Column 'requiere_pasajes_equipo' already exists")
        
        # Add requiere_vianda column if it doesn't exist
        if 'requiere_vianda' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN requiere_vianda BOOLEAN DEFAULT 0")
            print("Added 'requiere_vianda' column to reservations table")
        else:
            print("Column 'requiere_vianda' already exists")
        
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
    add_equipo_fields()
