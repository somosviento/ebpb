import sqlite3
import os

def add_research_team_site_fields():
    """
    Añade campos adicionales para el formulario de Equipos de Investigación:
    - sites_within_area: Sitios donde se desarrollarán las actividades dentro del área
    - requiere_discount_tickets: Requiere gestión de pasajes con descuento (ya existe como requiere_pasajes_equipo)
    - requiere_assistants: Requiere ayudantes y/o colaboradores (ya existe como requiere_ayudantes)
    - requiere_restaurant_services: Requieren servicio de vianda y/o utilizarán restaurante del Hotel Puerto Blest (ya existe como requiere_vianda)
    """
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
        
        # Add sites_within_area column if it doesn't exist
        if 'sites_within_area' not in columns:
            cursor.execute("ALTER TABLE reservations ADD COLUMN sites_within_area TEXT")
            print("Added 'sites_within_area' column to reservations table")
        else:
            print("Column 'sites_within_area' already exists")
        
        # The other fields already exist:
        # - requiere_ayudantes (requiere assistants)
        # - requiere_pasajes_equipo (discount tickets)
        # - requiere_vianda (restaurant services)
        print("Note: Other required fields already exist in the database schema:")
        print("- 'requiere_ayudantes' for 'Requiere ayudantes y/o colaboradores'")
        print("- 'requiere_pasajes_equipo' for 'Requiere gestión de pasajes con descuento'")
        print("- 'requiere_vianda' for 'Requieren servicio de vianda y/o utilizarán restaurante'")
        
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
    add_research_team_site_fields()
