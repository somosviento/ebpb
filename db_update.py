from __init__ import create_app, db
from models import User, Reservation, FechaReservada
from werkzeug.security import generate_password_hash
import os
import sys
from flask_migrate import Migrate

# Crear la aplicación
app = create_app()
migrate = Migrate(app, db)

def setup_database():
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        
        # Verificar si ya existe un usuario administrador
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("Creando usuario administrador predeterminado...")
            username = input("Nombre de usuario: ")
            email = input("Email: ")
            password = input("Contraseña: ")
            
            # Crear usuario administrador
            admin = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Usuario administrador '{username}' creado exitosamente!")
        else:
            print(f"Ya existe un usuario administrador: {admin.username}")
        
        # Actualizar el estado de las reservas existentes (si hay)
        reservations = Reservation.query.filter_by(estado=None).all()
        for reservation in reservations:
            reservation.estado = 'activa'
        if reservations:
            db.session.commit()
            print(f"Actualizadas {len(reservations)} reservas existentes con estado 'activa'")

if __name__ == "__main__":
    print("Configurando la base de datos...")
    setup_database()
    print("Base de datos configurada con éxito!")