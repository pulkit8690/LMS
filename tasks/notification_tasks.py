# tasks/notification_tasks.py

from celery_config import celery
from services.notification_service import NotificationService

@celery.task
def send_due_date_reminders_task():
    """Celery task to send due date reminders."""
    return NotificationService.send_due_date_reminders()

@celery.task
def send_fine_reminders_task():
    """Celery task to send fine reminders."""
    return NotificationService.send_fine_reminders()
