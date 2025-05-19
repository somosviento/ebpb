from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.models.reservation import Reservation
from app.models.participant import Participant
from app.models.reservation_date import ReservationDate
from app import db
from datetime import datetime, timedelta
from app.utils.pdf_generator import generate_pdf
from app.utils.google_drive import GoogleDriveService
from app.utils.date_helpers import daterange

form_bp = Blueprint('form', __name__, url_prefix='/form')

@form_bp.route('/reservation', methods=['GET', 'POST'])
def reservation_form():
    """Formulario unificado de reserva"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario principal
            person_in_charge = request.form.get('person_in_charge')
            dni = request.form.get('dni')
            phone = request.form.get('phone')
            email = request.form.get('email')
            alternative_email = request.form.get('alternative_email')
            postal_address = request.form.get('postal_address')
            institution = request.form.get('institution')
            reservation_type = request.form.get('reservation_type')
            parks_permit_number = request.form.get('parks_permit_number')
            
            # Crear nueva reserva
            new_reservation = Reservation(
                person_in_charge=person_in_charge,
                dni=dni,
                phone=phone,
                email=email,
                alternative_email=alternative_email,
                postal_address=postal_address,
                institution=institution,
                reservation_type=reservation_type,
                parks_permit_number=parks_permit_number
            )
            
            # Agregar campos específicos según el tipo de reserva
            if reservation_type == 'catedra':
                new_reservation.department = request.form.get('department')
                new_reservation.subject = request.form.get('subject')
            else:  # tipo equipo de investigación
                new_reservation.project_name = request.form.get('project_name')
                new_reservation.project_code = request.form.get('project_code')
                new_reservation.project_director = request.form.get('project_director')
                
                # Nuevos campos específicos para equipos
                new_reservation.activity_sites = ",".join(request.form.getlist('activity_sites[]')) if request.form.getlist('activity_sites[]') else None
                new_reservation.sites_within_area = request.form.get('sites_within_area')
                new_reservation.requiere_ayudantes = True if request.form.get('requiere_ayudantes') else False
                new_reservation.requiere_pasajes_equipo = True if request.form.get('requiere_pasajes_equipo') else False
                new_reservation.requiere_vianda = True if request.form.get('requiere_vianda') else False
            
            # Información adicional
            new_reservation.objetivos = request.form.get('objetivos')
            new_reservation.activity_details = request.form.get('activity_details')
            new_reservation.observations = request.form.get('observations')
            new_reservation.equipment = request.form.get('equipment')
            new_reservation.requiere_pasajes = True if request.form.get('requiere_pasajes') else False
            
            # Guardar la reserva para obtener el ID
            db.session.add(new_reservation)
            db.session.flush()
            
            # Procesar rango de fechas
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            date_range_people = request.form.get('date_range_people')
            
            if date_from and date_to and date_range_people:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                    range_people = int(date_range_people)
                    
                    # Verificar que date_to sea posterior a date_from
                    if date_to_obj >= date_from_obj:
                        # Usar la función daterange para iterar sobre el rango de fechas
                        for current_date in daterange(date_from_obj, date_to_obj):
                            # Para uso diurno siempre hay disponibilidad, pero verificamos por si acaso
                            if not check_availability(current_date, range_people, is_overnight=False):
                                flash(f'No hay disponibilidad para {range_people} personas en la fecha {current_date.strftime("%Y-%m-%d")} para uso diurno', 'danger')
                                db.session.rollback()
                                return render_template('form/reservation.html')
                            
                            # Crear fecha de reserva para el rango
                            reservation_date = ReservationDate(
                                reservation_id=new_reservation.id,
                                date=current_date,
                                num_people=range_people,
                                is_overnight=False,  # Días de rango son para uso diurno
                                purpose='uso diurno (rango)'  # Indicar que es parte de un rango
                            )
                            db.session.add(reservation_date)
                        
                        # Mensaje de confirmación del rango
                        flash(f'Se ha registrado un rango de fechas del {date_from} al {date_to} para {range_people} personas', 'success')
                    else:
                        flash('La fecha final debe ser igual o posterior a la fecha inicial', 'danger')
                        db.session.rollback()
                        return render_template('form/reservation.html')
                except ValueError as e:
                    flash(f'Error al procesar el rango de fechas: {str(e)}', 'danger')
                    db.session.rollback()
                    return render_template('form/reservation.html')
            
            # Procesar fechas de reserva individuales
            dates = request.form.getlist('date[]')
            num_people = request.form.getlist('num_people[]')
            
            for i in range(len(dates)):
                if dates[i] and num_people[i]:
                    date_obj = datetime.strptime(dates[i], '%Y-%m-%d').date()
                    people = int(num_people[i])
                    
                    # Verificar disponibilidad para esa fecha
                    if not check_availability(date_obj, people):
                        flash(f'No hay disponibilidad para {people} personas en la fecha {dates[i]}', 'danger')
                        db.session.rollback()
                        return render_template('form/reservation.html')
                    
                    # Crear fecha de reserva
                    reservation_date = ReservationDate(
                        reservation_id=new_reservation.id,
                        date=date_obj,
                        num_people=people,
                        is_overnight=True,  # Por defecto las fechas individuales son para pernoctar
                        purpose='pernoctar'
                    )
                    db.session.add(reservation_date)
            
            # Procesar participantes adicionales
            participant_names = request.form.getlist('participant_name[]')
            participant_dnis = request.form.getlist('participant_dni[]')
            participant_emails = request.form.getlist('participant_email[]')
            participant_phones = request.form.getlist('participant_phone[]')
            participant_roles = request.form.getlist('participant_role[]')
            participant_cuils = request.form.getlist('participant_cuil[]')
            participant_birth_dates = request.form.getlist('participant_birth_date[]')
            participant_institutions = request.form.getlist('participant_institution[]')
            participant_cargos = request.form.getlist('participant_cargo[]')
            participant_nacionalidades = request.form.getlist('participant_nacionalidad[]')
            
            for i in range(len(participant_names)):
                if participant_names[i] and participant_dnis[i]:
                    # Convertir la fecha de nacimiento si existe
                    birth_date = None
                    if i < len(participant_birth_dates) and participant_birth_dates[i]:
                        try:
                            birth_date = datetime.strptime(participant_birth_dates[i], '%Y-%m-%d').date()
                        except:
                            # Si hay error en el formato de la fecha, dejarlo como None
                            pass
                    
                    # Si es tipo equipo de investigación usamos los campos específicos, si no usamos los valores por defecto
                    if reservation_type == 'equipo':
                        participant_institution = participant_institutions[i] if i < len(participant_institutions) else institution
                        participant_cargo = participant_cargos[i] if i < len(participant_cargos) else None
                        participant_nacionalidad = participant_nacionalidades[i] if i < len(participant_nacionalidades) else None
                        participant_role = None  # No usamos rol para equipos
                    else:
                        participant_institution = institution
                        participant_cargo = None
                        participant_nacionalidad = None
                        participant_role = participant_roles[i] if i < len(participant_roles) else None
                    
                    participant = Participant(
                        reservation_id=new_reservation.id,
                        name=participant_names[i],
                        dni=participant_dnis[i],
                        email=participant_emails[i] if i < len(participant_emails) else None,
                        phone=participant_phones[i] if i < len(participant_phones) else None,
                        institution=participant_institution,
                        role=participant_role,
                        cuil=participant_cuils[i] if i < len(participant_cuils) else None,
                        birth_date=birth_date,
                        cargo=participant_cargo,
                        nacionalidad=participant_nacionalidad
                    )
                    db.session.add(participant)
            
            # Confirmar la transacción
            db.session.commit()
            
            # Generar PDF
            pdf_path = generate_pdf(new_reservation)
            
            # Crear instancia del servicio de Google Drive
            google_service = GoogleDriveService()
            
            # Intentar subir a Google Drive
            folder_name = f"{person_in_charge.split()[-1]}_{datetime.now().strftime('%Y%m%d')}"
            folder_id, folder_url = google_service.create_folder_and_upload(pdf_path, person_in_charge.split()[-1], datetime.now().strftime('%Y%m%d'))
            
            if folder_id:
                new_reservation.drive_folder_id = folder_id
            
            # Actualizar metadatos en la reserva (incluso si no se subió a Drive)
            new_reservation.pdf_path = pdf_path
            db.session.commit()
            
            # Enviar correo electrónico
            email_result = google_service.send_email(
                to_email="mpetrabissi@gmail.com",
                subject=f"Nueva reserva: {person_in_charge} - {datetime.now().strftime('%d/%m/%Y')}",
                html_body=f"""
                <p>Se ha registrado una nueva reserva para la Estación Biológica de Puerto Blest.</p>
                <p><strong>Responsable:</strong> {person_in_charge}<br>
                <strong>Tipo:</strong> {reservation_type}<br>
                <strong>Fechas:</strong> {', '.join(dates)}</p>
                """,
                attachment_ids=[folder_id] if folder_id else None
            )
            
            if not email_result.get('success'):
                flash('La reserva se registró correctamente pero hubo un problema al enviar el correo de confirmación.', 'warning')
            else:
                flash('Reserva enviada correctamente. Recibirá una confirmación por email.', 'success')
            
            return redirect(url_for('form.confirmation', reservation_id=new_reservation.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar el formulario: {str(e)}', 'danger')
    
    return render_template('form/reservation.html')

@form_bp.route('/confirmation/<int:reservation_id>')
def confirmation(reservation_id):
    """Página de confirmación después de enviar el formulario"""
    reservation = Reservation.query.get_or_404(reservation_id)
    return render_template('form/confirmation.html', reservation=reservation)

@form_bp.route('/check-availability', methods=['POST'])
def check_availability_endpoint():
    """Endpoint para verificar disponibilidad de fechas"""
    date_str = request.form.get('date')
    num_people = int(request.form.get('num_people', 1))
    reservation_id = request.form.get('reservation_id')
    is_overnight_str = request.form.get('is_overnight', 'true')
    
    # Convertimos el string a booleano
    is_overnight = is_overnight_str.lower() == 'true'
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Para uso diurno siempre hay disponibilidad
    if not is_overnight:
        return jsonify({
            'available': True,
            'remaining': 'Sin límite para uso diurno'
        })
    
    # Si estamos editando una reserva existente, excluimos su ocupación actual
    existing_occupancy = 0
    if reservation_id:
        from app.controllers.admin import get_existing_occupancy
        existing_occupancy = get_existing_occupancy(int(reservation_id), date_obj, is_overnight)
    
    # Calculamos la ocupación total excluyendo la reserva actual
    current_occupancy = get_occupancy(date_obj, is_overnight) - existing_occupancy
    available = (current_occupancy + num_people) <= 12
    
    return jsonify({
        'available': available,
        'remaining': 12 - current_occupancy if available else 0
    })

def check_availability(date, num_people, reservation_id=None, is_overnight=True):
    """
    Verifica si hay disponibilidad para una fecha y cantidad de personas.
    
    Args:
        date (date): Fecha a verificar
        num_people (int): Número de personas
        reservation_id (int, optional): ID de la reserva actual (para excluir en edición)
        is_overnight (bool, optional): Si la reserva es para pernoctar o solo uso diurno
        
    Returns:
        bool: True si hay disponibilidad, False en caso contrario
    """
    # Para uso diurno siempre hay disponibilidad, no hay límite estricto
    if not is_overnight:
        return True
        
    # Para pernoctar, verificar la ocupación
    current_occupancy = get_occupancy(date, is_overnight)
    
    # Si se proporciona el ID de la reserva, excluimos su ocupación actual
    if reservation_id:
        from app.controllers.admin import get_existing_occupancy
        existing_occupancy = get_existing_occupancy(reservation_id, date, is_overnight)
        current_occupancy -= existing_occupancy
        
    # La estación tiene capacidad máxima para 12 personas por noche
    return (current_occupancy + num_people) <= 12

def get_occupancy(date, is_overnight=True):
    """
    Obtiene la ocupación actual para una fecha específica
    
    Args:
        date (date): Fecha a consultar
        is_overnight (bool, optional): Si se calculará la ocupación para pernoctar o uso diurno
        
    Returns:
        int: Total de personas en esa fecha y tipo de uso
    """
    if is_overnight:
        # Contar solo las reservas para pernoctar
        reservations = ReservationDate.query.filter_by(date=date, is_overnight=True).all()
    else:
        # Contar solo las reservas de uso diurno
        reservations = ReservationDate.query.filter_by(date=date, is_overnight=False).all()
        
    return sum(r.num_people for r in reservations)