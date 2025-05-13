from datetime import datetime
from app import db

class ReservationDate(db.Model):
    __tablename__ = 'reservation_dates'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    
    # Fecha de la reserva
    date = db.Column(db.Date, nullable=False)
    
    # Número de personas para esa fecha específica
    num_people = db.Column(db.Integer, nullable=False, default=1)
    
    # Relación con la reserva principal
    reservation = db.relationship('Reservation', back_populates='date_ranges')
    
    def __repr__(self):
        return f'<ReservationDate {self.date}: {self.num_people} people>'