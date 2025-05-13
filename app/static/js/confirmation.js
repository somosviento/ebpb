// Función para inicializar todas las confirmaciones de acciones destructivas
function initConfirmations() {
    // Para botones o enlaces con el atributo data-confirm="true"
    document.addEventListener('click', function(event) {
        const target = event.target.closest('[data-confirm="true"]');
        if (target) {
            event.preventDefault();
            
            const message = target.getAttribute('data-confirm-message') || '¿Estás seguro que deseas realizar esta acción?';
            const title = target.getAttribute('data-confirm-title') || 'Confirmar acción';
            const confirmText = target.getAttribute('data-confirm-text') || 'Confirmar';
            const cancelText = target.getAttribute('data-confirm-cancel-text') || 'Cancelar';
            const confirmBtnClass = target.getAttribute('data-confirm-btn-class') || 'btn-danger';
            
            showConfirmationModal(title, message, function() {
                // Si es un botón de submit dentro de un formulario
                if (target.tagName === 'BUTTON' && target.type === 'submit') {
                    target.closest('form').submit();
                } 
                // Si es un enlace, redirigimos
                else if (target.tagName === 'A') {
                    window.location.href = target.href;
                }
                // Si tiene un callback personalizado
                else if (target.hasAttribute('data-confirm-callback')) {
                    const callbackName = target.getAttribute('data-confirm-callback');
                    if (typeof window[callbackName] === 'function') {
                        window[callbackName](target);
                    }
                }
            }, confirmText, cancelText, confirmBtnClass);
        }
    });

    // Inicializa los botones de eliminar fecha que ya tienen su propio comportamiento
    initRemoveDateButtons();
    
    // Inicializa los botones de eliminar participante
    initRemoveParticipantButtons();
}

// Función para mostrar el modal de confirmación
function showConfirmationModal(title, message, onConfirm, confirmText, cancelText, confirmBtnClass) {
    // Crear elementos del modal
    const modalId = 'confirmationModal' + Math.random().toString(36).substring(2);
    
    let modalFooter = '';
    if (cancelText) {
        // Si hay un texto de cancelación, mostramos ambos botones
        modalFooter = `
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                <button type="button" class="btn ${confirmBtnClass}" id="${modalId}ConfirmBtn">${confirmText}</button>
            </div>
        `;
    } else {
        // Si no hay texto de cancelación, solo mostramos el botón de confirmación
        modalFooter = `
            <div class="modal-footer">
                <button type="button" class="btn ${confirmBtnClass}" id="${modalId}ConfirmBtn" data-bs-dismiss="${!onConfirm ? 'modal' : ''}">${confirmText}</button>
            </div>
        `;
    }
    
    const modalHTML = `
        <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    ${modalFooter}
                </div>
            </div>
        </div>
    `;
    
    // Agregar el modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Obtener referencias a los elementos del modal
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);
    const confirmBtn = document.getElementById(`${modalId}ConfirmBtn`);
    
    // Configurar eventos
    confirmBtn.addEventListener('click', function() {
        modal.hide();
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    modalElement.addEventListener('hidden.bs.modal', function() {
        modalElement.remove();
    });
    
    // Mostrar el modal
    modal.show();
}

// Reemplazar el comportamiento del botón de eliminar fecha
function initRemoveDateButtons() {
    // Desvincula eventos anteriores para evitar duplicados
    $(document).off('click', '.remove-date');
    
    // Agrega el nuevo comportamiento
    $(document).on('click', '.remove-date', function() {
        const dateEntry = $(this).closest('.date-entry');
        const totalEntries = $('.date-entry').length;
        
        if (totalEntries > 1) {
            const dateText = dateEntry.find('.date-picker').val() || 'esta fecha';
            showConfirmationModal(
                'Eliminar fecha', 
                `¿Está seguro que desea eliminar ${dateText}?`, 
                function() {
                    dateEntry.remove();
                },
                'Eliminar',
                'Cancelar',
                'btn-danger'
            );        } else {
            // Mostrar un modal de alerta sin botón de cancelar
            showAlertModal(
                'Acción no permitida', 
                'Debe haber al menos una fecha de reserva. No se puede eliminar la única fecha disponible.',
                'Entendido',
                'btn-primary'
            );
        }
    });
}

// Reemplazar el comportamiento del botón de eliminar participante
function initRemoveParticipantButtons() {
    // Desvincula eventos anteriores para evitar duplicados
    $(document).off('click', '.remove-participant');
    
    // Agrega el nuevo comportamiento
    $(document).on('click', '.remove-participant', function() {
        const participantEntry = $(this).closest('.participant-entry');
        const participantName = participantEntry.find('input[name="participant_name[]"]').val() || 'este participante';
        
        showConfirmationModal(
            'Eliminar participante', 
            `¿Está seguro que desea eliminar a ${participantName}?`, 
            function() {
                participantEntry.remove();
            },
            'Eliminar',
            'Cancelar',
            'btn-danger'
        );
    });
}

// Función para mostrar un mensaje de alerta estilo modal (sin confirmación)
function showAlertModal(title, message, buttonText = 'Aceptar', buttonClass = 'btn-primary') {
    showConfirmationModal(title, message, null, buttonText, '', buttonClass);
}

// Reemplaza los alerts nativos del navegador con nuestro modal personalizado
function showCustomAlert(message) {
    showAlertModal('Aviso', message);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initConfirmations);
