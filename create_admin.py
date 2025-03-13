from __init__ import create_app, db
from models import User
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def create_admin_user(username=None, email=None, password=None):
    # Usar valores predeterminados del .env si no se proporcionan argumentos
    username = username or os.environ.get('DEFAULT_ADMIN_USERNAME')
    email = email or os.environ.get('DEFAULT_ADMIN_EMAIL')
    password = password or os.environ.get('DEFAULT_ADMIN_PASSWORD')
    
    if not all([username, email, password]):
        print("Error: Debe proporcionar username, email y password (ya sea como argumentos o en el archivo .env)")
        return False
    
    app = create_app()
    with app.app_context():
        # Verificar si ya existe un usuario con ese username o email
        if User.query.filter_by(username=username).first() is not None:
            print(f"Error: Ya existe un usuario con el nombre {username}")
            return False
            
        if User.query.filter_by(email=email).first() is not None:
            print(f"Error: Ya existe un usuario con el email {email}")
            return False
            
        # Crear el nuevo usuario administrador
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        print(f"Usuario administrador '{username}' creado exitosamente.")
        return True

if __name__ == "__main__":
    if len(sys.argv) == 4:
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
    else:
        print("Usando credenciales predeterminadas desde el archivo .env...")
        username = None
        email = None
        password = None
    
    if not create_admin_user(username, email, password):
        sys.exit(1)