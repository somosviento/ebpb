from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app.models.reservation import Reservation
from app.models.reservation_date import ReservationDate
from app.models.participant import Participant
from app.models.user import User
from app import db
import pandas as pd
import os
from datetime import datetime
from app.utils.pdf_generator import generate_pdf
from app.utils.google_drive import GoogleDriveService
from app.utils.date_helpers import daterange, group_consecutive_dates, group_date_ranges_by_people
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel de administración principal"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    # Obtener estadísticas
    total_reservations = Reservation.query.count()
    pending_reservations = Reservation.query.filter_by(status='pendiente').count()
    approved_reservations = Reservation.query.filter_by(status='aprobada').count()
    
    # Obtener reservas recientes
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                          total_reservations=total_reservations,
                          pending_reservations=pending_reservations,
                          approved_reservations=approved_reservations,
                          recent_reservations=recent_reservations)

@admin_bp.route('/reservations')
@login_required
def reservations():
    """Lista todas las reservas"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    # Filtrar por estado si se especifica
    status = request.args.get('status')
    
    if status:
        reservations = Reservation.query.filter_by(status=status).order_by(Reservation.created_at.desc()).all()
    else:
        reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    
    return render_template('admin/reservations.html', reservations=reservations, current_status=status)

@admin_bp.route('/reservation/<int:reservation_id>')
@login_required
def view_reservation(reservation_id):
    """Ver detalles de una reserva específica"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Separar fechas por tipo de uso
    overnight_dates = []
    day_use_dates = []
    day_use_ranges = []
    
    for date_range in reservation.date_ranges:
        if date_range.is_overnight:
            overnight_dates.append(date_range)
        elif date_range.purpose and 'rango' in date_range.purpose:
            day_use_ranges.append((date_range.date, date_range.num_people))
        else:
            day_use_dates.append(date_range)    # Agrupar fechas de rango
    range_groups = group_date_ranges_by_people(day_use_ranges)
    
    return render_template(
        'admin/reservation_detail_new.html', 
        reservation=reservation,
        overnight_dates=overnight_dates,
        day_use_dates=day_use_dates,
        range_groups=range_groups
    )

@admin_bp.route('/reservation/<int:reservation_id>/update-status', methods=['POST'])
@login_required
def update_reservation_status(reservation_id):
    """Actualizar el estado de una reserva"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    new_status = request.form.get('status')
    
    if new_status in ['pendiente', 'aprobada', 'rechazada', 'cancelada']:
        reservation.status = new_status
        db.session.commit()
        flash(f'Estado de la reserva actualizado a: {new_status}', 'success')
    else:
        flash('Estado no válido', 'danger')
    
    return redirect(url_for('admin.view_reservation', reservation_id=reservation_id))

@admin_bp.route('/reservation/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reservation(reservation_id):
    """Editar una reserva existente"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            reservation.person_in_charge = request.form.get('person_in_charge')
            reservation.dni = request.form.get('dni')
            reservation.phone = request.form.get('phone')
            reservation.email = request.form.get('email')
            reservation.alternative_email = request.form.get('alternative_email')
            reservation.postal_address = request.form.get('postal_address')
            reservation.institution = request.form.get('institution')
            reservation.parks_permit_number = request.form.get('parks_permit_number')
              # Actualizar el tipo de reserva (ahora permitimos cambiar el tipo)
            new_type = request.form.get('reservation_type')
            if new_type != reservation.reservation_type:
                # Si se cambia el tipo, limpiar campos específicos del tipo anterior
                if new_type == 'catedra':
                    # Limpiar campos de equipo de investigación
                    reservation.project_name = None
                    reservation.project_code = None
                    reservation.project_director = None
                    reservation.activity_sites = None
                    reservation.sites_within_area = None
                    reservation.requiere_ayudantes = False
                    reservation.requiere_pasajes_equipo = False
                    reservation.requiere_vianda = False
                else:  # cambio a equipo de investigación
                    # Limpiar campos de cátedra
                    reservation.department = None
                    reservation.subject = None
                
                # Actualizar el tipo
                reservation.reservation_type = new_type
            
            # Actualizar campos según el tipo de reserva (después del cambio)
            if reservation.reservation_type == 'catedra':
                reservation.department = request.form.get('department')
                reservation.subject = request.form.get('subject')
            else:  # tipo equipo de investigación
                reservation.project_name = request.form.get('project_name')
                reservation.project_code = request.form.get('project_code')
                reservation.project_director = request.form.get('project_director')
                reservation.activity_sites = ",".join(request.form.getlist('activity_sites[]')) if request.form.getlist('activity_sites[]') else None
                reservation.sites_within_area = request.form.get('sites_within_area')
                reservation.requiere_ayudantes = True if request.form.get('requiere_ayudantes') else False
                reservation.requiere_pasajes_equipo = True if request.form.get('requiere_pasajes_equipo') else False
                reservation.requiere_vianda = True if request.form.get('requiere_vianda') else False
              # Información adicional
            reservation.objetivos = request.form.get('objetivos')
            reservation.activity_details = request.form.get('activity_details')
            reservation.observations = request.form.get('observations')
            reservation.equipment = request.form.get('equipment')
            reservation.requiere_pasajes = True if request.form.get('requiere_pasajes') else False
            
            # Guardar cambios en la reserva principal
            db.session.commit()
            
            # Actualizar fechas de reserva
            # Primero, eliminar las fechas existentes
            for date in reservation.date_ranges:
                db.session.delete(date)
              # Luego, agregar las nuevas fechas
            from app.controllers.form import check_availability
            
            # Procesar fechas para pernoctar
            overnight_dates = request.form.getlist('overnight_date[]')
            overnight_people = request.form.getlist('overnight_num_people[]')
            
            for i in range(len(overnight_dates)):
                if overnight_dates[i] and overnight_people[i]:
                    date_obj = datetime.strptime(overnight_dates[i], '%Y-%m-%d').date()
                    people = int(overnight_people[i])
                    
                    # Verificar disponibilidad para esa fecha
                    if not check_availability(date_obj, people, reservation.id):
                        flash(f'No hay disponibilidad para {people} personas en la fecha {overnight_dates[i]}', 'danger')
                        db.session.rollback()
                        return redirect(url_for('admin.edit_reservation', reservation_id=reservation_id))
                    
                    # Crear fecha de reserva para pernoctar
                    reservation_date = ReservationDate(
                        reservation_id=reservation.id,
                        date=date_obj,
                        num_people=people,
                        is_overnight=True,
                        purpose='pernoctar'
                    )
                    db.session.add(reservation_date)
            
            # Procesar fechas individuales para uso diurno
            day_use_dates = request.form.getlist('day_use_date[]')
            day_use_people = request.form.getlist('day_use_num_people[]')
            
            for i in range(len(day_use_dates)):
                if day_use_dates[i] and day_use_people[i]:
                    date_obj = datetime.strptime(day_use_dates[i], '%Y-%m-%d').date()
                    people = int(day_use_people[i])
                    
                    # Verificar disponibilidad para esa fecha (para uso diurno)
                    if not check_availability(date_obj, people, reservation.id, is_overnight=False):
                        flash(f'No hay disponibilidad para {people} personas en la fecha {day_use_dates[i]} para uso diurno', 'danger')
                        db.session.rollback()
                        return redirect(url_for('admin.edit_reservation', reservation_id=reservation_id))
                    
                    # Crear fecha de reserva para uso diurno
                    reservation_date = ReservationDate(
                        reservation_id=reservation.id,
                        date=date_obj,
                        num_people=people,
                        is_overnight=False,
                        purpose='uso diurno'
                    )
                    db.session.add(reservation_date)
            
            # Procesar rango de fechas para uso diurno
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            date_range_people = request.form.get('date_range_people')
            
            if date_from and date_to and date_range_people:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                people = int(date_range_people)
                
                # Crear una entrada para cada día en el rango
                for single_date in daterange(start_date, end_date):
                    # Verificar disponibilidad para cada fecha del rango
                    if not check_availability(single_date, people, reservation.id, is_overnight=False):
                        flash(f'No hay disponibilidad para {people} personas en la fecha {single_date.strftime("%Y-%m-%d")} para uso diurno', 'danger')
                        db.session.rollback()
                        return redirect(url_for('admin.edit_reservation', reservation_id=reservation_id))
                    
                    # Crear fecha de reserva para uso diurno en el rango
                    reservation_date = ReservationDate(
                        reservation_id=reservation.id,
                        date=single_date,
                        num_people=people,
                        is_overnight=False,
                        purpose='uso diurno (rango)'
                    )
                    db.session.add(reservation_date)
            
            # Actualizar participantes
            # Primero, eliminar los participantes existentes
            for participant in reservation.participants:
                db.session.delete(participant)            # Luego, agregar los nuevos participantes
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
                            pass  # Si hay un error, dejamos la fecha como None
                      # Usar los campos adecuados según el tipo de reserva (después del posible cambio)
                    if reservation.reservation_type == 'equipo':
                        participant_institution = participant_institutions[i] if i < len(participant_institutions) else reservation.institution
                        participant_cargo = participant_cargos[i] if i < len(participant_cargos) else None
                        participant_nacionalidad = participant_nacionalidades[i] if i < len(participant_nacionalidades) else None
                        participant_role = None  # No usamos rol para equipos
                    else:
                        participant_institution = reservation.institution  # Para cátedras usamos la misma institución
                        participant_cargo = None
                        participant_nacionalidad = None
                        participant_role = participant_roles[i] if i < len(participant_roles) else None
                    
                    participant = Participant(
                        reservation_id=reservation.id,
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
            
            # Confirmar cambios
            db.session.commit()
            
            # Regenerar PDF
            pdf_path = generate_pdf(reservation)
            reservation.pdf_path = pdf_path
            
            # Si la reserva ya tiene folder_id en Drive, intentar actualizar el archivo
            if reservation.drive_folder_id:
                try:
                    file_name = f"{reservation.person_in_charge.split()[-1]}_{datetime.now().strftime('%Y%m%d')}_formulario.pdf"
                    
                    # Usar el servicio de Google Drive
                    google_service = GoogleDriveService()
                    
                    # Llamar al método create_folder_and_upload con los parámetros adecuados
                    folder_id, folder_url = google_service.create_folder_and_upload(
                        pdf_path, 
                        reservation.person_in_charge.split()[-1], 
                        datetime.now().strftime('%Y%m%d')
                    )
                    
                    # No actualizamos el drive_folder_id aquí para mantener el ID original
                except Exception as e:
                    # Si falla la subida, solo lo registramos pero no interrumpimos el proceso
                    print(f"Error al subir PDF a Google Drive: {str(e)}")
            
            db.session.commit()
            
            flash('Reserva actualizada correctamente', 'success')
            return redirect(url_for('admin.view_reservation', reservation_id=reservation_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la reserva: {str(e)}', 'danger')
    
    return render_template('admin/edit_reservation_updated.html', reservation=reservation)

@admin_bp.route('/reservation/<int:reservation_id>/delete', methods=['POST'])
@login_required
def delete_reservation(reservation_id):
    """Eliminar una reserva"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    try:
        db.session.delete(reservation)  # Esto eliminará también fechas y participantes por la cascada
        db.session.commit()
        flash('Reserva eliminada correctamente', 'success')
        return redirect(url_for('admin.reservations'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la reserva: {str(e)}', 'danger')
        return redirect(url_for('admin.view_reservation', reservation_id=reservation_id))

@admin_bp.route('/export-excel')
@login_required
def export_excel():
    """Exportar reservas a Excel"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    # Obtener todas las reservas
    reservations = Reservation.query.all()
    
    # Preparar datos para Excel
    data = []
    for reservation in reservations:        # Crear un registro por cada fecha de reserva
        for date_range in reservation.date_ranges:
            # Determinar el tipo de uso
            if date_range.is_overnight:
                uso_tipo = "Pernocte"
            else:
                uso_tipo = "Uso diurno"
                if date_range.purpose and "rango" in date_range.purpose:
                    uso_tipo += " (rango)"
            
            record = {
                'ID': reservation.id,
                'Responsable': reservation.person_in_charge,
                'DNI': reservation.dni,
                'Email': reservation.email,
                'Teléfono': reservation.phone,
                'Institución': reservation.institution,
                'Tipo': reservation.reservation_type,
                'Permiso PN': reservation.parks_permit_number or 'N/A',
                'Fecha': date_range.date.strftime('%d/%m/%Y'),
                'Tipo de uso': uso_tipo,
                'Personas': date_range.num_people,
                'Estado': reservation.status,
                'Fecha de creación': reservation.created_at.strftime('%d/%m/%Y %H:%M')
            }
            
            # Agregar campos específicos según el tipo
            if reservation.reservation_type == 'catedra':
                record['Departamento'] = reservation.department or 'N/A'
                record['Asignatura'] = reservation.subject or 'N/A'
                record['Proyecto'] = 'N/A'
                record['Código Proyecto'] = 'N/A'
                record['Director'] = 'N/A'
            else:
                record['Departamento'] = 'N/A'
                record['Asignatura'] = 'N/A'
                record['Proyecto'] = reservation.project_name or 'N/A'
                record['Código Proyecto'] = reservation.project_code or 'N/A'
                record['Director'] = reservation.project_director or 'N/A'
            
            data.append(record)
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Crear el directorio de exportaciones si no existe
    exports_dir = os.path.join(current_app.root_path, 'static', 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    # Guardar a Excel usando la ruta correcta
    filename = f'reservas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    excel_file = os.path.join(exports_dir, filename)
    df.to_excel(excel_file, index=False)
    
    return send_file(excel_file, as_attachment=True, download_name=filename)

@admin_bp.route('/export-dates-csv/<int:reservation_id>')
@login_required
def export_dates_csv(reservation_id):
    """Exporta las fechas de una reserva específica a un archivo CSV"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Preparar datos para CSV
    data = []
    for date_range in reservation.date_ranges:
        uso_tipo = "Pernocte" if date_range.is_overnight else "Uso diurno"
        if date_range.purpose and "rango" in date_range.purpose:
            uso_tipo += " (rango)"
        
        data.append({
            'Fecha': date_range.date.strftime('%d/%m/%Y'),
            'Tipo de uso': uso_tipo,
            'Personas': date_range.num_people
        })
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Crear el directorio de exportaciones si no existe
    exports_dir = os.path.join(current_app.root_path, 'static', 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    # Guardar a CSV
    filename = f'fechas_reserva_{reservation_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    csv_file = os.path.join(exports_dir, filename)
    df.to_csv(csv_file, index=False)
    
    return send_file(csv_file, as_attachment=True, download_name=filename)

def get_existing_occupancy(reservation_id, date, is_overnight=True):
    """
    Obtiene la ocupación actual para una fecha y reserva específica
    
    Args:
        reservation_id (int): ID de la reserva
        date (date): Fecha a consultar
        is_overnight (bool, optional): Si se calculará la ocupación para pernoctar o uso diurno
        
    Returns:
        int: Total de personas en esa fecha, reserva y tipo de uso
    """
    reservation_dates = ReservationDate.query.filter_by(
        reservation_id=reservation_id,
        date=date,
        is_overnight=is_overnight
    ).all()
    return sum(rd.num_people for rd in reservation_dates)

def get_occupancy(date, is_overnight=True):
    """
    Obtiene la ocupación total para una fecha específica y tipo de uso
    
    Args:
        date (date): Fecha a consultar
        is_overnight (bool, optional): Si se calculará la ocupación para pernoctar o uso diurno
        
    Returns:
        int: Total de personas en esa fecha y tipo de uso
    """
    reservations = ReservationDate.query.filter_by(date=date, is_overnight=is_overnight).all()
    return sum(r.num_people for r in reservations)

# Gestión de usuarios

@admin_bp.route('/users')
@login_required
def manage_users():
    """Administración de usuarios"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.order_by(User.name).all()
    return render_template('admin/user/list.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """Añadir nuevo usuario"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = True if request.form.get('is_admin') else False
        
        # Validaciones
        if not name or not email or not password:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template('admin/user/add.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('admin/user/add.html')
            
        # Verificar si el correo ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Ya existe un usuario con ese correo electrónico', 'danger')
            return render_template('admin/user/add.html')
        
        try:
            # Crear nuevo usuario
            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                is_admin=is_admin
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el usuario: {str(e)}', 'danger')
    
    return render_template('admin/user/add.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Editar usuario existente"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = True if request.form.get('is_admin') else False
        
        # Validaciones
        if not name or not email:
            flash('Nombre y correo son campos obligatorios', 'danger')
            return render_template('admin/user/edit.html', user=user)
        
        # Verificar si el correo ya existe (excepto para el usuario actual)
        existing_user = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_user:
            flash('Ya existe otro usuario con ese correo electrónico', 'danger')
            return render_template('admin/user/edit.html', user=user)
        
        try:
            # Actualizar datos básicos
            user.name = name
            user.email = email
            user.is_admin = is_admin
            
            # Actualizar contraseña solo si se proporciona una nueva
            if password:
                if password != confirm_password:
                    flash('Las contraseñas no coinciden', 'danger')
                    return render_template('admin/user/edit.html', user=user)
                user.password = generate_password_hash(password)
            
            db.session.commit()
            
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el usuario: {str(e)}', 'danger')
    
    return render_template('admin/user/edit.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Eliminar usuario"""
    if not current_user.is_admin:
        flash('Acceso denegado. Necesitas permisos de administrador.', 'danger')
        return redirect(url_for('main.index'))
    
    # No permitir eliminar al propio usuario
    if user_id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))