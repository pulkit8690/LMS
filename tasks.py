from services.notification_service import NotificationService  # ✅ Removed `backend.`
from app import celery

@celery.task
def send_due_date_reminders_task():
    """Celery task to send due date reminders."""
    with celery.app.app_context():  # ✅ Ensures the task runs in Flask's app context
        return NotificationService.send_due_date_reminders()

@celery.task
def send_fine_reminders_task():
    """Celery task to send fine reminders."""
    with celery.app.app_context():  # ✅ Ensures the task runs in Flask's app context
        return NotificationService.send_fine_reminders()
