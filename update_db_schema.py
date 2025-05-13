import sqlite3
import os

# Path to your SQLite database
db_path = os.path.join('instance', 'ebpb.db')

try:
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(reservations)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add the alternative_email column if it doesn't exist
    if 'alternative_email' not in columns:
        cursor.execute("ALTER TABLE reservations ADD COLUMN alternative_email TEXT")
        print("Column 'alternative_email' added successfully to reservations table")
    else:
        print("Column 'alternative_email' already exists in reservations table")
    
    # Add the postal_address column if it doesn't exist
    if 'postal_address' not in columns:
        cursor.execute("ALTER TABLE reservations ADD COLUMN postal_address TEXT DEFAULT 'No especificado' NOT NULL")
        print("Column 'postal_address' added successfully to reservations table")
    else:
        print("Column 'postal_address' already exists in reservations table")
    
    # Commit the changes
    conn.commit()
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
finally:
    # Close the connection
    if conn:
        conn.close()

print("Database update completed.")
