from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import db, Note, PasswordResetToken, User
import json
from .auth import send_reset_password_email, generate_reset_token
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from .forms import CreateNoteForm, EditNoteForm


views = Blueprint('views', __name__)

csrf = CSRFProtect()

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 5

    notes = Note.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    pagination = notes

    form = CreateNoteForm()

    if form.validate_on_submit():
        note = form.note.data
        category = form.category.data
        reminder_datetime_str = form.reminder.data

        if reminder_datetime_str and not isinstance(reminder_datetime_str, str):
            # Si reminder_datetime_str no es una cadena, conviértelo a cadena
            reminder_datetime_str = reminder_datetime_str.strftime('%Y-%m-%dT%H:%M')
            try:
                if reminder_datetime_str:
                    reminder_datetime = datetime.strptime(reminder_datetime_str, '%Y-%m-%dT%H:%M')
                else:
                    reminder_datetime = None
            except ValueError:
                flash('Error al parsear la fecha del recordatorio')
                return render_template("home.html", user=current_user, notes=notes.items, pagination=pagination, form=form)

        if not note:
            flash('Note cannot be empty!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, category=category, reminder=reminder_datetime)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            return redirect(url_for('views.home'))


    return render_template("home.html", user=current_user, notes=notes.items, pagination=pagination, form=form)

@views.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token or reset_token.expiry_time < datetime.utcnow():
        flash('El enlace de restablecimiento de contraseña es inválido o ha expirado.', 'error')
        return redirect(url_for('views.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
        else:
            # Actualiza la contraseña del usuario y elimina el token de restablecimiento
            user = User.query.get(reset_token.user_id)
            user.set_password(new_password)
            db.session.delete(reset_token)
            db.session.commit()

            flash('Contraseña restablecida con éxito. Puedes iniciar sesión con tu nueva contraseña.', 'success')
            return redirect(url_for('views.login'))

    return render_template('reset_password.html', token=token)
    # Lógica para resetear la contraseña utilizando el token
    # ...

@views.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Genera un token de restablecimiento de contraseña y envía el correo electrónico
            token = generate_reset_token(user)
            send_reset_password_email(user, token)
            flash('Se ha enviado un correo electrónico con las instrucciones para restablecer la contraseña.', 'success')
            return redirect(url_for('views.login'))
        else:
            flash('No se encontró ninguna cuenta asociada a ese correo electrónico.', 'error')

    return render_template('forgot_password.html')

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


@views.route('/edit_note/<int:note_id>', methods=['POST'])
def edit_note_modal(note_id):
    note_to_edit = Note.query.get_or_404(note_id)
    form = EditNoteForm(obj=note_to_edit)

    if request.method == 'POST' and form.validate_on_submit():
        note_content = form.note.data
        category = form.category.data
        reminder_datetime_str = form.reminder.data

        if reminder_datetime_str and not isinstance(reminder_datetime_str, str):
            # Si reminder_datetime_str no es una cadena, conviértelo a cadena
            reminder_datetime_str = reminder_datetime_str.strftime('%Y-%m-%dT%H:%M')

        
            try:
                if reminder_datetime_str:
                    reminder_datetime = datetime.strptime(reminder_datetime_str, '%Y-%m-%dT%H:%M')
                else: 
                    reminder_datetime = None
            except ValueError:
                return jsonify({'error': 'Error parsing reminder date'})
        

        if not note_content:
            return jsonify({'error': 'Note cannot be empty!'})

        note_to_edit.data = note_content
        note_to_edit.category = category
        note_to_edit.reminder = reminder_datetime

        print("Valor de 'note' antes de la validación:", note_content)
        print("Valor de 'category' antes de la validación:", category)
        print("Valor de 'reminder' antes de la validación:", reminder_datetime_str)

        db.session.commit()
        flash('Note updated successfully!', category='success')
        return redirect(url_for('views.home'))
        

    return jsonify({'error': 'Invalid request'})

""" @views.route('/edit_note/<int:note_id>', methods=['POST'])
def edit_note(note_id):
    note = Note.query.filter_by(id=note_id).first()

    if note is None:
        return jsonify({'message': 'Nota no encontrada'}), 404
    
    print("Valor de 'note' antes de la validación:", note)
    
    if request.is_json:
        data = request.get_json()
        new_data = data.get('edited_note', '')
        new_category = data.get('edited_category', '')
        new_reminder_datetime_str = data.get('edited_reminder', '')
        print(data)

        try:
            if new_reminder_datetime_str:
                new_reminder_datetime = datetime.strptime(new_reminder_datetime_str, '%Y-%m-%dT%H:%M')
            else:
                new_reminder_datetime = None
        except ValueError as e:
            current_app.logger.error(f'Error parsing reminder date: {str(e)}')
            return jsonify({'message': 'Error al parsear la fecha del recordatorio'}), 400

        # Elimina el trabajo anterior si existe
        existing_job_id = f'note_{note_id}_reminder'
        existing_job = scheduler.get_job(existing_job_id)
        if existing_job:
            scheduler.remove_job(existing_job_id)

            
         # Genera un identificador único para el trabajo
        job_id = f'note_{note_id}_reminder_{uuid4()}'

        # Agrega el nuevo trabajo
        try:
            note.data = new_data
            note.category = new_category
            note.reminder = new_reminder_datetime  # Asigna el nuevo valor al campo de recordatorio

            db.session.commit()

            if new_reminder_datetime is not None:
                print(f"Scheduling reminder for note {note_id}")
                print(new_category)
                # job_id = f'note_{note_id}_reminder_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'

                existing_job = scheduler.get_job(job_id)
                if existing_job:
                    scheduler.remove_job(job_id)

                print(f"Adding job with ID: {job_id}")

                scheduler.add_job(schedule_reminder, args=[note_id,new_reminder_datetime, new_data, new_category], id=job_id, replace=True)
                print(new_category, new_data, new_reminder_datetime)
            
             # Enviar la nota actualizada directamente en la respuesta
            updated_note = {
                'id': note.id,
                'content': note.data,
                'category': note.category,
                'reminder': note.reminder.strftime('%Y-%m-%dT%H:%M') if note.reminder else None,
                # Agregar más campos según la estructura de tu modelo de nota
            }


            # En tu vista de Flask, después de editar la nota exitosamente
            socketio.emit('note_updated', {'note_id': note_id, 'updated_note': updated_note}, namespace='/', room=current_user.id)

            response = jsonify({'message': 'Nota editada correctamente', 'updated_note': updated_note})
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        except ValueError as e:
            error_message = f'Error en la función edit_note: {str(e)}'
            print(error_message)
            current_app.logger.error(error_message)
            return jsonify({'message': f'Error al editar la nota: {str(e)}'}), 400
        except Exception as e:
            error_message = f'Error en la función edit_note: {str(e)}'
            print(error_message)  # Imprimir el mensaje de error en la consola
            current_app.logger.error(error_message)
            return jsonify({'message': f'Error al editar la nota: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Unsupported Media Type'}), 415
     """

@views.route('/get_note/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = Note.query.get(note_id)

    if note:
        # Convierte la nota a un diccionario para que pueda ser serializado a JSON
        note_data = {
            'id': note.id,
            'content': note.content,
            'category': note.category,
            'reminder': note.reminder.strftime('%Y-%m-%dT%H:%M') if note.reminder else None,
            # Agrega más campos según la estructura de tu modelo de nota
        }
        return jsonify(note_data), 200
    else:
        return jsonify({'message': 'Nota no encontrada'}), 404

@views.route('/cancel-edit/<int:note_id>', methods=['POST'])
def cancel_edit(note_id):
    # Lógica para cancelar la edición de la nota con el ID note_id
    return jsonify({'message': 'Edición cancelada'}), 200

@views.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')

    # Lógica para realizar la búsqueda en la base de datos
    notes = Note.query.filter(
        (Note.user_id == current_user.id) &
        ((Note.data.contains(query)) | (Note.category.contains(query)))
    ).all()

    return render_template("search_results.html", user=current_user, notes=notes, query=query)