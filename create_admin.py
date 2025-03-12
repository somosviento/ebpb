from __init__ import create_app, db
from models import User
import sys

def create_admin_user(username, email, password):
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
    if len(sys.argv) != 4:
        print("Uso: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    if not create_admin_user(username, email, password):
        sys.exit(1)