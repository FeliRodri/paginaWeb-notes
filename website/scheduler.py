from flask_apscheduler import APScheduler
from apscheduler.schedulers.base import JobLookupError
import uuid

scheduler = APScheduler()

def send_notification(note_id, new_data, new_category, new_reminder_datetime):
    # Puedes personalizar esta función para enviar notificaciones a través de diferentes canales (correo electrónico, mensajes, etc.)
    print(f"¡Recordatorio! Nota ID: {note_id}")
    print(f"Data: {new_data}")
    print(f"Categoría: {new_category}")
    print(f"Fecha de recordatorio: {new_reminder_datetime}")

def schedule_reminder(note_id, new_reminder_datetime, new_data, new_category):
    job_id = f'note_{note_id}_reminder_{str(uuid.uuid4())}'


    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)
    # Intentar eliminar cualquier trabajo existente para la nota
    try:
        scheduler.remove_job(job_id)
    except JobLookupError:
        pass  # No hacer nada si el trabajo no existe

    try:
        scheduler.add_job(
            send_notification,
            trigger='date',
            run_date=new_reminder_datetime,
            args=[note_id, new_data, new_category, new_reminder_datetime],
            id=job_id,
            replace_existing=True
        )
        print(f"Scheduled reminder for note {note_id}")
    except JobLookupError as e:
        print(f"Error al programar el recordatorio: {e}")

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
