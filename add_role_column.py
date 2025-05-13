import sqlite3
import os

# Path to the database file
database_path = 'instance/ebpb.db'
full_path = os.path.join(os.getcwd(), database_path)

print(f"Current working directory: {os.getcwd()}")
print(f"Looking for database at: {full_path}")

def add_role_column():
    # Connect to the SQLite database
    try:
        if not os.path.exists(full_path):
            print(f"Error: Database file not found at {full_path}")
            return
            
        print(f"Connecting to database: {full_path}")
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute('PRAGMA table_info(participants)')
        columns = cursor.fetchall()
        print(f"Current columns in participants table: {columns}")
        column_names = [col[1] for col in columns]
        
        if 'role' not in column_names:
            print("Adding 'role' column to participants table...")
            # Add the role column to the participants table
            cursor.execute('ALTER TABLE participants ADD COLUMN role VARCHAR(50)')
            conn.commit()
            print("Column 'role' added successfully!")
        else:
            print("Column 'role' already exists in participants table.")
            
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    add_role_column()
