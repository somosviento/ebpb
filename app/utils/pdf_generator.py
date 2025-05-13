from fpdf import FPDF
import os
from datetime import datetime

class ReservationPDF(FPDF):
    def header(self):
        # Logo
        self.image('app/static/img/logo.png', 10, 8, 33) if os.path.exists('app/static/img/logo.png') else None
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Mover a la derecha
        self.cell(80)
        # Título
        self.cell(30, 10, 'Estación Biológica de Puerto Blest', 0, 0, 'C')
        # Salto de línea
        self.ln(20)

    def footer(self):
        # Posición a 1.5 cm desde abajo
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Número de página
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        
def generate_pdf(reservation):
    """Genera un PDF para una reserva específica"""
    # Crear directorio si no existe
    pdf_dir = os.path.join('app', 'static', 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Nombre del archivo
    filename = f"{reservation.person_in_charge.split()[-1]}_{datetime.now().strftime('%Y%m%d')}_formulario.pdf"
    filepath = os.path.join(pdf_dir, filename)
    
    # Inicializar PDF
    pdf = ReservationPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Tipo de formulario
    if reservation.reservation_type == 'catedra':
        pdf.cell(0, 10, 'FORMULARIO DE RESERVA - CÁTEDRAS', 0, 1, 'C')
    else:
        pdf.cell(0, 10, 'FORMULARIO DE RESERVA - EQUIPO DE INVESTIGACIÓN', 0, 1, 'C')
    
    pdf.ln(10)
    
    # Información del responsable
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'INFORMACIÓN DEL RESPONSABLE', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    pdf.cell(60, 8, 'Nombre y Apellido:', 0, 0)
    pdf.cell(0, 8, reservation.person_in_charge, 0, 1)
    
    pdf.cell(60, 8, 'DNI / Pasaporte:', 0, 0)
    pdf.cell(0, 8, reservation.dni, 0, 1)
    
    pdf.cell(60, 8, 'Teléfono:', 0, 0)
    pdf.cell(0, 8, reservation.phone, 0, 1)
    
    pdf.cell(60, 8, 'Email:', 0, 0)
    pdf.cell(0, 8, reservation.email, 0, 1)
    
    pdf.cell(60, 8, 'Institución:', 0, 0)
    pdf.cell(0, 8, reservation.institution, 0, 1)
    
    pdf.cell(60, 8, 'Permiso Parques Nacionales:', 0, 0)
    pdf.cell(0, 8, reservation.parks_permit_number or 'No especificado', 0, 1)
    
    pdf.ln(5)
    
    # Información adicional según el tipo de reserva
    pdf.set_font('Arial', 'B', 12)
    if reservation.reservation_type == 'catedra':
        pdf.cell(0, 10, 'INFORMACIÓN DE LA CÁTEDRA', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        pdf.cell(60, 8, 'Departamento:', 0, 0)
        pdf.cell(0, 8, reservation.department or 'No especificado', 0, 1)
        
        pdf.cell(60, 8, 'Asignatura:', 0, 0)
        pdf.cell(0, 8, reservation.subject or 'No especificado', 0, 1)
    else:
        pdf.cell(0, 10, 'INFORMACIÓN DEL PROYECTO', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        pdf.cell(60, 8, 'Nombre del Proyecto:', 0, 0)
        pdf.cell(0, 8, reservation.project_name or 'No especificado', 0, 1)
        
        pdf.cell(60, 8, 'Código del Proyecto:', 0, 0)
        pdf.cell(0, 8, reservation.project_code or 'No especificado', 0, 1)
        
        pdf.cell(60, 8, 'Director del Proyecto:', 0, 0)
        pdf.cell(0, 8, reservation.project_director or 'No especificado', 0, 1)
    
    pdf.ln(5)
    
    # Fechas de reserva
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'FECHAS DE RESERVA', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    for date_range in reservation.date_ranges:
        pdf.cell(60, 8, 'Fecha:', 0, 0)
        pdf.cell(60, 8, date_range.date.strftime('%d/%m/%Y'), 0, 0)
        pdf.cell(40, 8, 'Personas:', 0, 0)
        pdf.cell(0, 8, str(date_range.num_people), 0, 1)
    
    pdf.ln(5)
    
    # Participantes
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'PARTICIPANTES', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Responsable (siempre incluido)
    pdf.cell(60, 8, '1. ' + reservation.person_in_charge, 0, 0)
    pdf.cell(0, 8, reservation.dni, 0, 1)
    
    # Otros participantes
    for i, participant in enumerate(reservation.participants, 2):
        pdf.cell(60, 8, f'{i}. {participant.name}', 0, 0)
        pdf.cell(0, 8, participant.dni, 0, 1)
    
    pdf.ln(5)
    
    # Detalles de la actividad
    if reservation.activity_details:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'DETALLES DE LA ACTIVIDAD', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        # Texto multilínea
        pdf.multi_cell(0, 8, reservation.activity_details)
        pdf.ln(5)
    
    # Equipamiento
    if reservation.equipment:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'EQUIPAMIENTO', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        # Texto multilínea
        pdf.multi_cell(0, 8, reservation.equipment)
        pdf.ln(5)
    
    # Observaciones
    if reservation.observations:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'OBSERVACIONES', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        # Texto multilínea
        pdf.multi_cell(0, 8, reservation.observations)
    
    # Guardar PDF
    pdf.output(filepath)
    
    return filepath