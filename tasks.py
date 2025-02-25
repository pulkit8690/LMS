from celery import shared_task
from services.notification_service import NotificationService

@shared_task(bind=True)
def send_due_date_reminders_task(self):
    """Celery task to send due date reminders."""
    try:
        return NotificationService.send_due_date_reminders()
    except Exception as e:
        self.retry(exc=e, countdown=10)
        return {"error": f"Task failed: {str(e)}"}

@shared_task(bind=True)
def send_fine_reminders_task(self):
    """Celery task to send fine reminders."""
    try:
        return NotificationService.send_fine_reminders()
    except Exception as e:
        self.retry(exc=e, countdown=10)
        return {"error": f"Task failed: {str(e)}"}
