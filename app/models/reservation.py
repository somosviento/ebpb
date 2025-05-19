from datetime import datetime
from app import db

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del responsable
    person_in_charge = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    alternative_email = db.Column(db.String(120), nullable=True)
    postal_address = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    
    # Tipo de reserva (cátedra o equipo de investigación)
    reservation_type = db.Column(db.String(50), nullable=False)
    
    # Número de permiso de Parques Nacionales (campo adicional)
    parks_permit_number = db.Column(db.String(50), nullable=True)
    
    # Información académica
    department = db.Column(db.String(200), nullable=True)  # Para cátedras
    subject = db.Column(db.String(200), nullable=True)     # Para cátedras
    project_name = db.Column(db.String(500), nullable=True)  # Para equipos de investigación
    project_code = db.Column(db.String(100), nullable=True)  # Para equipos de investigación
    project_director = db.Column(db.String(100), nullable=True)  # Para equipos de investigación
    
    # Información adicional
    objetivos = db.Column(db.Text, nullable=True)  # Nuevo campo para objetivos
    activity_details = db.Column(db.Text, nullable=True)
    observations = db.Column(db.Text, nullable=True)
    equipment = db.Column(db.Text, nullable=True)
    requiere_pasajes = db.Column(db.Boolean, default=False)  # Nuevo campo para gestión de pasajes
    
    # Campos específicos para equipos de investigación
    activity_sites = db.Column(db.String(255), nullable=True)  # Sitios donde se desarrollarán las actividades
    requiere_ayudantes = db.Column(db.Boolean, default=False)  # Requiere ayudantes/colaboradores
    requiere_pasajes_equipo = db.Column(db.Boolean, default=False)  # Requiere pasajes con descuento
    requiere_vianda = db.Column(db.Boolean, default=False)  # Requiere servicio de vianda
    
    # Estado de la reserva
    status = db.Column(db.String(20), default='pendiente')  # pendiente, aprobada, rechazada, cancelada
    
    # Fechas de registro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadatos
    pdf_path = db.Column(db.String(255), nullable=True)
    drive_folder_id = db.Column(db.String(255), nullable=True)
    
    # Relaciones
    date_ranges = db.relationship('ReservationDate', back_populates='reservation', cascade='all, delete-orphan')
    participants = db.relationship('Participant', back_populates='reservation', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Reservation {self.id}: {self.person_in_charge}>'
    
    def get_total_people(self):
        """Obtiene el número total de personas en la reserva, incluido el responsable"""
        return len(self.participants) + 1
    
    def is_editable(self):
        """Determina si la reserva puede ser editada"""
        return self.status in ['pendiente', 'aprobada']