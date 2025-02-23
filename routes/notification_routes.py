from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.notification_service import NotificationService
from tasks import send_due_date_reminders_task, send_fine_reminders_task

notification_bp = Blueprint("notification", __name__)

# ✅ Manually Trigger Due Date Reminders
@notification_bp.route("/send-due-reminders", methods=["POST"])
@jwt_required()
def send_due_reminders():
    """Triggers due date reminders manually."""
    return jsonify(NotificationService.send_due_date_reminders())

# ✅ Manually Trigger Fine Reminders
@notification_bp.route("/send-fine-reminders", methods=["POST"])
@jwt_required()
def send_fine_reminders():
    """Triggers fine reminders manually."""
    return jsonify(NotificationService.send_fine_reminders())

# ✅ Schedule Automatic Email Reminders (Celery)
@notification_bp.route("/schedule-due-reminders", methods=["POST"])
def schedule_due_reminders():
    """Schedules automatic due date reminders via Celery."""
    send_due_date_reminders_task.apply_async()
    return jsonify({"message": "Scheduled due date reminders"}), 200

@notification_bp.route("/schedule-fine-reminders", methods=["POST"])
def schedule_fine_reminders():
    """Schedules automatic fine reminders via Celery."""
    send_fine_reminders_task.apply_async()
    return jsonify({"message": "Scheduled fine reminders"}), 200
