from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

# Import the NotificationService and Celery tasks
from services.notification_service import NotificationService
from tasks.notification_tasks import send_due_date_reminders_task, send_fine_reminders_task

notification_bp = Blueprint("notification", __name__)

# ✅ Manually Trigger Due Date Reminders
@notification_bp.route("/send-due-reminders", methods=["POST"])
@jwt_required()
def send_due_reminders():
    """Triggers due date reminders manually."""
    result = NotificationService.send_due_date_reminders()
    
    # ✅ Ensure `result` is a dictionary, not a Response object
    if isinstance(result, tuple):  # Expected (dict, status_code)
        response, status_code = result
    else:  # Handle cases where only a dict is returned
        response, status_code = result, 200

    return jsonify(response), status_code

# ✅ Manually Trigger Fine Reminders
@notification_bp.route("/send-fine-reminders", methods=["POST"])
@jwt_required()
def send_fine_reminders():
    """Triggers fine reminders manually."""
    result = NotificationService.send_fine_reminders()

    if isinstance(result, tuple):  
        response, status_code = result
    else:  
        response, status_code = result, 200

    return jsonify(response), status_code
