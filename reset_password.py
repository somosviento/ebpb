from __init__ import create_app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    app = create_app()
    with app.app_context():
        # Buscar el usuario administrador
        admin = User.query.filter_by(username='mpetrabissi').first()
        if admin:
            # Establecer nueva contraseña
            nueva_password = 'admin123'  # Puedes cambiar esto por la contraseña que desees
            admin.password_hash = generate_password_hash(nueva_password)
            db.session.commit()
            print(f"Contraseña restablecida para el usuario {admin.username}")
            print(f"Nueva contraseña: {nueva_password}")
        else:
            print("Usuario administrador no encontrado")

if __name__ == "__main__":
    reset_admin_password()