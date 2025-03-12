from __init__ import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='activa')  # 'activa', 'cancelada'
    
    # Datos institucionales
    institucion = db.Column(db.String(200), nullable=False)
    objetivos = db.Column(db.Text)
    antecedentes = db.Column(db.Text)
    actividad = db.Column(db.Text, nullable=False)
    finalidad = db.Column(db.String(100))
    
    # Archivos adjuntos
    permiso_file = db.Column(db.String(200))
    integrantes_file = db.Column(db.String(200))
    
    # Datos de alojamiento
    pernoctar = db.Column(db.Boolean, default=False)
    # Las fechas se manejan en la tabla FechaReservada
    
    # Datos de actividades
    sitios = db.Column(db.String(200))  # Almacenados como CSV
    infraestructuras = db.Column(db.String(200))  # Almacenados como CSV
    requiere_ayudantes = db.Column(db.Boolean, default=False)
    requiere_pasajes = db.Column(db.Boolean, default=False)
    requiere_alojamiento = db.Column(db.Boolean, default=False)
    alojamiento_detalles = db.Column(db.Text)
    requiere_vianda = db.Column(db.Boolean, default=False)
    otras_aclaraciones = db.Column(db.Text)
    
    # Datos de contacto
    responsable_nombre = db.Column(db.String(100), nullable=False)
    responsable_dni = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    email_alternativo = db.Column(db.String(100))
    telefono = db.Column(db.String(30), nullable=False)
    direccion_postal = db.Column(db.String(200))
    
    # Relación con las fechas reservadas
    fechas_reservadas = db.relationship('FechaReservada', backref='reserva', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Reservation {self.id} - {self.responsable_nombre}>'

class FechaReservada(db.Model):
    __tablename__ = 'fechas_reservadas'
    
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<FechaReservada {self.fecha} - {self.cantidad_personas} personas>'
    
    @classmethod
    def verificar_disponibilidad(cls, fecha, cantidad_solicitada=1):
        """Verifica la disponibilidad para una fecha específica.
        
        Args:
            fecha: La fecha a verificar.
            cantidad_solicitada: Cantidad de lugares solicitados.
            
        Returns:
            dict: Diccionario con información sobre disponibilidad.
        """
        # Capacidad máxima por noche
        CAPACIDAD_MAXIMA = 12
        
        # Consultar cuántos lugares están ocupados para esta fecha (solo en reservas activas)
        ocupados = db.session.query(db.func.sum(cls.cantidad_personas)).\
            join(Reservation, cls.reserva_id == Reservation.id).\
            filter(cls.fecha == fecha, Reservation.estado == 'activa').scalar() or 0
        
        # Calcular disponibles
        disponibles = CAPACIDAD_MAXIMA - ocupados
        
        # Verificar si hay suficiente disponibilidad
        disponible = disponibles >= cantidad_solicitada
        
        return {
            'fecha': fecha.strftime('%Y-%m-%d'),
            'ocupados': ocupados,
            'disponibles': disponibles,
            'solicitados': cantidad_solicitada,
            'disponible': disponible
        }