function showDeleteConfirmation(noteId) {
        // Abre el modal de confirmación
        $('#deleteConfirmationModal').modal('show');

        // Asigna el ID de la nota al botón de confirmación del modal
        $('#deleteConfirmationModal .btn-danger').attr('data-note-id', noteId);
    }


function deleteNote() {

    var noteId = $('#deleteConfirmationModal .btn-danger').attr('data-note-id');
    var csrfToken = $('[name="csrf_token"]').attr('value');

    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({ noteId: noteId }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
    })
    .then((res) => {
        if (!res.ok) {
            throw new Error('Error al eliminar la nota.');
        }
        return res.json();
    })
    .then((_res) => {

        $('#deleteConfirmationModal').modal('hide');

        window.location.href = "/";
    })
    .catch((error) => {
        console.error(error);
    });
}

$(document).ready(function () {

    // Evento cuando el modal de Crear Notas se muestra
    $('#crearNotaModal').on('show.bs.modal', function (event) {
        console.log('El modal de Crear Notas se está mostrando');
        // Puedes realizar acciones adicionales cuando el modal se muestra
    });

    // Evento cuando el modal de Crear Notas se oculta
    $('#crearNotaModal').on('hidden.bs.modal', function (event) {
        console.log('El modal de Crear Notas se ha ocultado');
        // Puedes realizar acciones adicionales cuando el modal se oculta
    });
    
    $('.edit-note-btn').click(function () {
        var noteId = $(this).data('note-id');

        // Realiza una solicitud AJAX para obtener los detalles de la nota
        $.ajax({
            url: '/edit_note_modal/' + noteId,
            type: 'GET',
            success: function (response) {
                // Abre el modal y carga los detalles de la nota
                // response.note_content, response.category, response.reminder
                // puedes utilizar estos valores para rellenar el formulario del modal
            },
            error: function (error) {
                console.error('Error:', error.responseText);
            }
        });
    });
});
// Asigna el evento clic a los elementos de la lista de notas
/* $(document).on('click', '.list-group-item', function () {
    // Obtiene los datos de la nota desde los atributos de datos del elemento clicado
    const noteId = $(this).data('note-id');
    const noteData = $(this).data('note-data');
    const noteCategory = $(this).data('note-category');
    const noteReminder = $(this).data('note-reminder');

    // Llama a la función para mostrar el modal
    showEditModal(noteId, noteData, noteCategory, noteReminder);
});
 */
function showEditModal(noteId, noteData, noteCategory, noteReminder) {
    // Coloca los valores actuales en los campos del modal
    $('#editedNoteData').val(noteData);
    $('#editedNoteCategory').val(noteCategory);
    
    if (noteReminder) {
        const formattedReminder = new Date(noteReminder).toISOString().slice(0, 16);
        $('#editedNoteReminder').val(formattedReminder);
    } else {
        $('#editedNoteReminder').val('');
    }

    $('#editNoteModal .btn-primary').attr('data-note-id', noteId);

    // Muestra el modal
    $('#editNoteModal').modal('show');
}

$('#editNoteModal .btn-primary').on('click', function () {
    // Obtiene el noteId del botón
    const noteId = $(this).data('note-id');
    // Llama a la función para actualizar la nota
    updateNote(noteId);
});

function updateNote(noteId) {
    var editedNoteData = document.getElementById(`editedNoteData${noteId}`).value;
    var editedNoteCategory = document.getElementById(`editedNoteCategory${noteId}`).value;
    var editedReminder = document.getElementById(`editedNoteReminder${noteId}`).value;

    if (!editedNoteData || !editedNoteCategory || !editedReminder) {
        console.error('El contenido editado de la nota no puede estar vacío.');
        return false;
    }

    var data = {
        edited_note: editedNoteData,
        edited_category: editedNoteCategory,
        edited_reminder: editedReminder,
    };

    data = Object.fromEntries(Object.entries(data).filter(([_, v]) => v));
    var csrfToken = $('[name="csrf_token"]').attr('value');


    fetch(`/edit_note/${noteId}?_=${Date.now()}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al actualizar la nota.');
        }
        return response.json();
    })
    .then(response => {
        console.log(response);
        console.log(`Función updateNote ejecutada para la nota con ID: ${noteId}`);

        var updatedNote = response.updated_note

        if(updatedNote) {

            if (updatedNote.data) {
                document.getElementById(`editedNoteData${noteId}`).value = updatedNote.data;
            }
            if (updatedNote.category) {
                document.getElementById(`editedNoteCategory${noteId}`).value = updatedNote.category;
            }
            if (updatedNote.reminder) {
                document.getElementById(`editedNoteReminder${noteId}`).value = updatedNote.reminder;
            }

        }

        

        document.getElementById(`edit_form_${noteId}`).style.display = 'none';

        window.location.href = "/";
    })
    .catch(error => {
        console.error('Error al actualizar la nota:', error);
    });

    return false;
}

$('#editNoteModal .btn-primary').on('click', function () {
    // Obtiene el noteId del botón
    const noteId = $(this).data('note-id');
    // Llama a la función para actualizar la nota
    updateNote(noteId);
});

function cancelEdit(noteId) {
    document.getElementById(`edit_form_${noteId}`).style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    var protocol = location.protocol;
    var domain = location.hostname;
    var port = location.port || (protocol === 'https:' ? '443' : '80');
    var socket = io.connect(`${protocol}//${domain}:${port}`);

    socket.on('note_updated', function (data) {
        const updatedNote = data.updated_note;
        console.log('Nota actualizada:', updatedNote);

        // No es necesario realizar otra solicitud para obtener la nota actualizada
        updateNoteInUI(data.updated_note);
    });

    function updateNoteInUI(updatedNote) {
        var noteId = updatedNote.id;

        // Verificar si el elemento existe antes de intentar actualizarlo
        var editedNoteElement = document.getElementById(`editedNoteData${noteId}`);
        var editedCategoryElement = document.getElementById(`editedNoteCategory${noteId}`);
        var editedReminderElement = document.getElementById(`editedNoteReminder${noteId}`);

        if (editedNoteElement && editedCategoryElement && editedReminderElement) {
            // Actualizar el contenido de la nota en el DOM
            if (updatedNote.data) {
                editedNoteElement.value = updatedNote.data;
            }
            if (updatedNote.category) {
                editedCategoryElement.value = updatedNote.category;
            }
            if (updatedNote.reminder) {
                editedReminderElement.value = updatedNote.reminder;
            }
        } else {
            console.error('Elementos de nota no encontrados en el DOM.');
        }
    }
});