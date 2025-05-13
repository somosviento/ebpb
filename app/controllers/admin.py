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
    return render_template('admin/reservation_detail.html', reservation=reservation)

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
            
            # Actualizar campos según el tipo de reserva
            if reservation.reservation_type == 'catedra':
                reservation.department = request.form.get('department')
                reservation.subject = request.form.get('subject')
            else:  # tipo equipo de investigación
                reservation.project_name = request.form.get('project_name')
                reservation.project_code = request.form.get('project_code')
                reservation.project_director = request.form.get('project_director')
            
            # Información adicional
            reservation.activity_details = request.form.get('activity_details')
            reservation.observations = request.form.get('observations')
            reservation.equipment = request.form.get('equipment')
            
            # Guardar cambios en la reserva principal
            db.session.commit()
            
            # Actualizar fechas de reserva
            # Primero, eliminar las fechas existentes
            for date in reservation.date_ranges:
                db.session.delete(date)
            
            # Luego, agregar las nuevas fechas
            dates = request.form.getlist('date[]')
            num_people = request.form.getlist('num_people[]')
            
            for i in range(len(dates)):
                if dates[i] and num_people[i]:
                    date_obj = datetime.strptime(dates[i], '%Y-%m-%d').date()
                    people = int(num_people[i])
                      # Verificar disponibilidad para esa fecha
                    from app.controllers.form import check_availability
                    if not check_availability(date_obj, people, reservation.id):
                        flash(f'No hay disponibilidad para {people} personas en la fecha {dates[i]}', 'danger')
                        db.session.rollback()
                        return redirect(url_for('admin.edit_reservation', reservation_id=reservation_id))
                    
                    # Crear fecha de reserva
                    reservation_date = ReservationDate(
                        reservation_id=reservation.id,
                        date=date_obj,
                        num_people=people
                    )
                    db.session.add(reservation_date)
            
            # Actualizar participantes
            # Primero, eliminar los participantes existentes
            for participant in reservation.participants:
                db.session.delete(participant)
              # Luego, agregar los nuevos participantes
            participant_names = request.form.getlist('participant_name[]')
            participant_dnis = request.form.getlist('participant_dni[]')
            participant_emails = request.form.getlist('participant_email[]')
            participant_phones = request.form.getlist('participant_phone[]')
            participant_roles = request.form.getlist('participant_role[]')
            
            for i in range(len(participant_names)):
                if participant_names[i] and participant_dnis[i]:
                    participant = Participant(
                        reservation_id=reservation.id,
                        name=participant_names[i],
                        dni=participant_dnis[i],
                        email=participant_emails[i] if i < len(participant_emails) else None,
                        phone=participant_phones[i] if i < len(participant_phones) else None,
                        institution=reservation.institution,
                        role=participant_roles[i] if i < len(participant_roles) else None
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
    
    return render_template('admin/edit_reservation.html', reservation=reservation)

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
    for reservation in reservations:
        # Crear un registro por cada fecha de reserva
        for date_range in reservation.date_ranges:
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

def get_existing_occupancy(reservation_id, date):
    """Obtiene la ocupación actual para una fecha y reserva específica"""
    reservation_dates = ReservationDate.query.filter_by(
        reservation_id=reservation_id,
        date=date
    ).all()
    return sum(rd.num_people for rd in reservation_dates)

def get_occupancy(date):
    """Obtiene la ocupación actual para una fecha específica"""
    reservations = ReservationDate.query.filter_by(date=date).all()
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