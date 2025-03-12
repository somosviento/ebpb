// Funcionalidad principal para el formulario EBPB

document.addEventListener('DOMContentLoaded', () => {
    // Añadir validación del formulario antes de envío
    const form = document.getElementById('reservationForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Verificar si hay fechas seleccionadas cuando se requiere pernoctar
            const pernoctar = document.getElementById('pernoctar');
            const fechasReserva = document.getElementById('fechas_reserva_input');
            
            if (pernoctar && pernoctar.checked && (!fechasReserva.value || fechasReserva.value === '')) {
                e.preventDefault();
                alert('Por favor seleccione al menos una fecha para pernoctar.');
                return false;
            }
            
            // Validar campos requeridos
            const camposRequeridos = [
                'institucion', 'actividad', 'responsable_nombre', 
                'responsable_dni', 'email', 'telefono'
            ];
            
            let faltanCampos = false;
            
            camposRequeridos.forEach(campo => {
                const elemento = document.getElementById(campo);
                if (elemento && (!elemento.value || elemento.value.trim() === '')) {
                    faltanCampos = true;
                    elemento.classList.add('is-invalid');
                } else if (elemento) {
                    elemento.classList.remove('is-invalid');
                }
            });
            
            if (faltanCampos) {
                e.preventDefault();
                alert('Por favor complete todos los campos obligatorios marcados con *');
                return false;
            }
        });
    }
    
    // Inicializar tooltips de Bootstrap (si se usan)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Función para formatear fechas en español
    window.formatearFecha = function(fecha) {
        const opciones = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        };
        return new Date(fecha).toLocaleDateString('es-ES', opciones);
    };

    // Función para ajustar la altura de los textareas automáticamente
    const autoResizeTextareas = () => {
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });
    };
    
    autoResizeTextareas();
});