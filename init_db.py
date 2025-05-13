import os
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def init_db():
    """Inicializa la base de datos y crea el usuario administrador"""
    app = create_app()
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Verificar si ya existe un usuario administrador
        admin = User.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first()
        if not admin:
            admin = User(
                email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
                password=generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123')),
                name='Administrador',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Usuario administrador creado exitosamente.')
        else:
            print('El usuario administrador ya existe.')

if __name__ == '__main__':
    init_db()
    print('Base de datos inicializada correctamente.')