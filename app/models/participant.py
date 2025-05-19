from datetime import datetime
from app import db

class Participant(db.Model):
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
      # Información del participante
    name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    cuil = db.Column(db.String(20), nullable=True)  # Nuevo campo CUIL
    birth_date = db.Column(db.Date, nullable=True)  # Nuevo campo fecha de nacimiento
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    institution = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(50), nullable=True)  # Mantener por compatibilidad
    cargo = db.Column(db.String(100), nullable=True)  # Nuevo campo cargo
    nacionalidad = db.Column(db.String(100), nullable=True)  # Nuevo campo nacionalidad
    
    # Relación con la reserva
    reservation = db.relationship('Reservation', back_populates='participants')
    
    def __repr__(self):
        return f'<Participant {self.name} ({self.dni})>'