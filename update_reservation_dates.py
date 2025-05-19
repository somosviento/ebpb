import sqlite3
import os

print("Current working directory:", os.getcwd())
print("Looking for database at:", os.path.abspath("instance/ebpb.db"))

if os.path.exists("instance/ebpb.db"):
    print("Database file found!")
else:
    print("Database file NOT found!")
    possible_locations = [
        "instance/ebpb.db",
        "../instance/ebpb.db",
        "./ebpb.db",
        "ebpb.db"
    ]
    for loc in possible_locations:
        if os.path.exists(loc):
            print(f"Found database at: {loc}")
            db_path = loc
            break
    else:
        print("Could not find the database file!")
        db_path = "instance/ebpb.db"  # Default

try:
    print(f"Trying to connect to: {db_path}")
    conn = sqlite3.connect("instance/ebpb.db")
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:", [table[0] for table in tables])
    
    # Check if the table exists
    if ('reservation_dates',) not in tables:
        print("Error: reservation_dates table does not exist!")
    else:
        print("reservation_dates table found!")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(reservation_dates)")
        columns_info = cursor.fetchall()
        columns = [column[1] for column in columns_info]
        print("Current columns:", columns)
        
        if 'is_overnight' not in columns:
            print("Adding 'is_overnight' column...")
            cursor.execute('ALTER TABLE reservation_dates ADD COLUMN is_overnight BOOLEAN DEFAULT 0 NOT NULL')
        else:
            print("'is_overnight' column already exists")
        
        if 'purpose' not in columns:
            print("Adding 'purpose' column...")
            cursor.execute('ALTER TABLE reservation_dates ADD COLUMN purpose VARCHAR(50)')
        else:
            print("'purpose' column already exists")
        
        conn.commit()
        
        # Verify the columns were added
        cursor.execute("PRAGMA table_info(reservation_dates)")
        columns_info = cursor.fetchall()
        columns = [f"{column[1]} ({column[2]})" for column in columns_info]
        print(f"Updated columns in reservation_dates: {columns}")
        
        print("Database schema update completed successfully!")
except Exception as e:
    print(f"Error updating database schema: {str(e)}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
