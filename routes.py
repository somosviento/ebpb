from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from datetime import datetime
import os
import json
from __init__ import db
from models import Reservation, FechaReservada, User
from forms import ReservationForm, LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    @app.route('/')
    def index():
        # Pasar el año actual para el pie de página
        return render_template('index.html', now=datetime.now())

    @app.route('/formulario', methods=['GET', 'POST'])
    def formulario():
        form = ReservationForm()
        if form.validate_on_submit():
            # Procesamiento de archivos adjuntos
            permiso_file = None
            integrantes_file = None
            
            if form.permiso_file.data:
                permiso_file = save_file(form.permiso_file.data, app)
            
            if form.integrantes_file.data:
                integrantes_file = save_file(form.integrantes_file.data, app)
                
            # Crear nueva reserva
            reservation = Reservation(
                institucion=form.institucion.data,
                objetivos=form.objetivos.data,
                antecedentes=form.antecedentes.data,
                actividad=form.actividad.data,
                finalidad=','.join(form.finalidad.data) if isinstance(form.finalidad.data, list) else form.finalidad.data,
                permiso_file=permiso_file,
                integrantes_file=integrantes_file,
                pernoctar=form.pernoctar.data,
                sitios=','.join(form.sitios.data) if isinstance(form.sitios.data, list) else form.sitios.data,
                infraestructuras=','.join(form.infraestructuras.data) if isinstance(form.infraestructuras.data, list) else form.infraestructuras.data,
                requiere_ayudantes=form.requiere_ayudantes.data,
                requiere_pasajes=form.requiere_pasajes.data,
                requiere_alojamiento=form.requiere_alojamiento.data,
                alojamiento_detalles=form.alojamiento_detalles.data,
                requiere_vianda=form.requiere_vianda.data,
                otras_aclaraciones=form.otras_aclaraciones.data,
                responsable_nombre=form.responsable_nombre.data,
                responsable_dni=form.responsable_dni.data,
                email=form.email.data,
                email_alternativo=form.email_alternativo.data,
                telefono=form.telefono.data,
                direccion_postal=form.direccion_postal.data
            )
            
            # Guardar fechas reservadas con diferentes cantidades por fecha
            if form.pernoctar.data and form.fechas_reserva.data:
                try:
                    fechas_data = json.loads(form.fechas_reserva.data)
                    
                    if not fechas_data:
                        flash('Debe seleccionar al menos una fecha para pernoctar', 'danger')
                        return render_template('formulario.html', form=form, now=datetime.now())
                    
                    for fecha_item in fechas_data:
                        fecha_str = fecha_item.get('fecha')
                        cantidad = fecha_item.get('cantidad', 1)
                        
                        if not fecha_str or not cantidad:
                            continue
                            
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                        
                        # Verificar disponibilidad antes de guardar
                        disponibilidad = FechaReservada.verificar_disponibilidad(fecha, cantidad)
                        if not disponibilidad['disponible']:
                            flash(f'No hay suficiente disponibilidad para la fecha {fecha_str}', 'danger')
                            return render_template('formulario.html', form=form, now=datetime.now())
                        
                        # Guardar la fecha reservada
                        fecha_reservada = FechaReservada(
                            reserva=reservation,
                            fecha=fecha,
                            cantidad_personas=cantidad
                        )
                        db.session.add(fecha_reservada)
                except json.JSONDecodeError:
                    flash('Error en el formato de las fechas seleccionadas', 'danger')
                    return render_template('formulario.html', form=form, now=datetime.now())
                except Exception as e:
                    flash(f'Error al procesar las fechas: {str(e)}', 'danger')
                    return render_template('formulario.html', form=form, now=datetime.now())
            
            db.session.add(reservation)
            db.session.commit()
            flash('Formulario enviado con éxito!', 'success')
            return redirect(url_for('index'))
        
        return render_template('formulario.html', form=form, now=datetime.now())

    @app.route('/verificar_disponibilidad')
    def verificar_disponibilidad():
        fecha = request.args.get('fecha')
        cantidad = request.args.get('cantidad', 1, type=int)
        
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                disponibilidad = FechaReservada.verificar_disponibilidad(fecha_obj, cantidad)
                return jsonify(disponibilidad)
            except ValueError:
                return jsonify({"error": "Formato de fecha inválido"}), 400
        return jsonify({"error": "Fecha no proporcionada"}), 400

    # Rutas para gestión de usuarios
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Usuario o contraseña incorrectos', 'danger')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        return render_template('login.html', form=form, now=datetime.now())

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/register', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data, is_admin=True)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Nuevo administrador registrado exitosamente!', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('register.html', form=form, now=datetime.now())
    
    # Rutas para gestión de reservas (admin)
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        reservas = Reservation.query.all()
        return render_template('admin/dashboard.html', reservas=reservas, now=datetime.now())
    
    @app.route('/admin/reserva/<int:id>')
    @login_required
    @admin_required
    def ver_reserva(id):
        reserva = Reservation.query.get_or_404(id)
        return render_template('admin/ver_reserva.html', reserva=reserva, now=datetime.now())
    
    @app.route('/admin/reserva/<int:id>/cancelar', methods=['POST'])
    @login_required
    @admin_required
    def cancelar_reserva(id):
        reserva = Reservation.query.get_or_404(id)
        reserva.estado = 'cancelada'
        db.session.commit()
        flash(f'Reserva #{id} cancelada exitosamente', 'success')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/calendario')
    @login_required
    @admin_required
    def calendario_reservas():
        # Obtener todas las fechas reservadas para el calendario
        fechas = FechaReservada.query.join(
            Reservation, FechaReservada.reserva_id == Reservation.id
        ).filter(Reservation.estado == 'activa').all()
        
        eventos = []
        for f in fechas:
            # Determinar color basado en ocupación
            ocupacion = (f.cantidad_personas / 12) * 100  # 12 es la capacidad máxima
            if ocupacion >= 90:
                color = '#dc3545'  # Rojo para alta ocupación
            elif ocupacion >= 50:
                color = '#ffc107'  # Amarillo para ocupación media
            else:
                color = '#28a745'  # Verde para baja ocupación
            
            eventos.append({
                'title': f"{f.reserva.institucion} ({f.cantidad_personas} personas)",
                'start': f.fecha.strftime('%Y-%m-%d'),
                'url': url_for('ver_reserva', id=f.reserva.id),
                'backgroundColor': color,
                'borderColor': color,
            })
        
        return render_template('admin/calendario.html', eventos=eventos, now=datetime.now())

def save_file(file, app):
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None