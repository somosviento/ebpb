import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime
import jinja2

# Inicializar SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    # Cargar variables de entorno
    load_dotenv()
      # Inicializar la aplicación Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///ebpb.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Habilitar extensión 'do' en Jinja2
    app.jinja_env.add_extension('jinja2.ext.do')
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar el login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    
    # Agregar filtro nl2br para convertir saltos de línea a <br>
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if text:
            return jinja2.utils.markupsafe.Markup(text.replace('\n', '<br>'))
        return ''
    
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Context processor para añadir variables globales a las plantillas
    @app.context_processor
    def utility_processor():
        return {'now': datetime.now()}
    
    # Registrar blueprints
    from app.controllers.main import main_bp
    from app.controllers.auth import auth_bp
    from app.controllers.form import form_bp
    from app.controllers.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(admin_bp)
    
    return app