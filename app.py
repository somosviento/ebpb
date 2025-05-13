from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
import os
import click

# Crear la aplicación Flask
app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Inicializa la base de datos y crea el usuario administrador."""
    with app.app_context():
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
            click.echo('Usuario administrador creado exitosamente.')
        else:
            click.echo('El usuario administrador ya existe.')
    
    click.echo('Base de datos inicializada correctamente.')

@app.shell_context_processor
def make_shell_context():
    """Proporciona un contexto para el shell de Flask."""
    return {
        'db': db, 
        'User': User,
    }

if __name__ == '__main__':
    app.run(debug=True)