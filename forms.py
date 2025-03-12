from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, SelectMultipleField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, EqualTo, Length, ValidationError
from wtforms.widgets import HiddenInput
from models import User

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor use un nombre de usuario diferente.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor use un correo electrónico diferente.')

class ReservationForm(FlaskForm):
    # Datos institucionales
    institucion = StringField('Institución', validators=[DataRequired()])
    objetivos = TextAreaField('Objetivos')
    antecedentes = TextAreaField('Antecedentes')
    actividad = TextAreaField('Actividad a desarrollar', validators=[DataRequired()])
    finalidad = SelectMultipleField('Finalidad', choices=[
        ('investigacion', 'Investigación'), 
        ('curso', 'Curso'), 
        ('salida_catedra', 'Salida de Cátedra'), 
        ('otro', 'Otro')
    ])
    
    # Archivos adjuntos
    permiso_file = FileField('Permiso de Parques Nacionales (adjuntar archivo)')
    integrantes_file = FileField('Integrantes (adjuntar archivo)')
    
    # Datos de alojamiento
    pernoctar = BooleanField('¿Necesitarán pernoctar?')
    fechas_reserva = StringField('Fechas seleccionadas', widget=HiddenInput())
    cantidad_personas = StringField('Cantidad de personas', default='1')
    
    # Datos de actividades
    sitios = SelectMultipleField('Sitios donde desarrollará sus actividades dentro del área', 
                        choices=[
                            ('bosque', 'Bosque'),
                            ('lago', 'Lago'),
                            ('rio', 'Río'),
                            ('otro', 'Otro')
                        ])
    
    infraestructuras = SelectMultipleField('Infraestructuras a utilizar',
                                choices=[
                                    ('laboratorio', 'Laboratorio'),
                                    ('casa_huespedes', 'Casa de huéspedes'),
                                    ('ninguna', 'Ninguna'),
                                    ('otra', 'Otra')
                                ])
    
    requiere_ayudantes = BooleanField('¿Requiere de ayudantes y/o colaboradores?')
    requiere_pasajes = BooleanField('¿Requiere gestión de pasajes con descuento?')
    requiere_alojamiento = BooleanField('¿Requiere alojamiento con descuento en Hotel Puerto Blest?')
    alojamiento_detalles = TextAreaField('Detalles del alojamiento')
    requiere_vianda = BooleanField('¿Requiere servicio de vianda y/o utilizará restaurant del Hotel?')
    otras_aclaraciones = TextAreaField('Otras aclaraciones que desee realizar')
    
    # Datos de contacto
    responsable_nombre = StringField('Apellido y Nombre del responsable designado', validators=[DataRequired()])
    responsable_dni = StringField('DNI', validators=[DataRequired()])
    email = StringField('E-mail principal', validators=[DataRequired(), Email()])
    email_alternativo = StringField('E-mail alternativo', validators=[Optional(), Email()])
    telefono = StringField('Tel/Celular', validators=[DataRequired()])
    direccion_postal = StringField('Dirección Postal')