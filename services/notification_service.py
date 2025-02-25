from flask_mail import Message
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from flask import jsonify

# Import the single db instance
from models import db
from extensions import mail  # If your mail is defined in extensions.py
from models.transaction_model import BorrowedBook
from models.notification_model import NotificationLog
from models.user_model import User

class NotificationService:
    """Handles sending due date and fine reminders."""

    @staticmethod
    def send_email(recipient, subject, body):
        """Sends an email notification."""
        msg = Message(subject, recipients=[recipient])
        msg.body = body

        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False

    @staticmethod
    def send_due_date_reminders():
        """Sends reminders for books due in 2 days."""
        reminder_date = datetime.utcnow() + timedelta(days=2)
        try:
            borrowed_books = BorrowedBook.query.filter(
                BorrowedBook.due_date <= reminder_date,
                BorrowedBook.returned.is_(False)
            ).all()

            reminders_sent = 0

            for record in borrowed_books:
                user = User.query.get(record.user_id)
                if not user:
                    continue

                message = (
                    f"Reminder: Your borrowed book '{record.book.title}' is due on "
                    f"{record.due_date.strftime('%Y-%m-%d')}. Please return it on time to avoid fines."
                )

                if NotificationService.send_email(user.email, "Library Due Date Reminder", message):
                    log = NotificationLog(
                        user_id=user.id,
                        message=message,
                        notification_type="due_date"
                    )
                    db.session.add(log)
                    reminders_sent += 1

            db.session.commit()
            return {"message": f"Due date reminders sent to {reminders_sent} users"}, 200  # ✅ JSON-safe dict

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500  # ✅ JSON-safe dict

    @staticmethod
    def send_fine_reminders():
        """Sends reminders for unpaid fines."""
        try:
            overdue_fines = BorrowedBook.query.filter(
                BorrowedBook.fine_amount > 0,
                BorrowedBook.fine_paid.is_(False)
            ).all()

            reminders_sent = 0

            for record in overdue_fines:
                user = User.query.get(record.user_id)
                if not user:
                    continue

                message = (
                    f"Reminder: You have an unpaid fine of ₹{record.fine_amount}. "
                    "Please pay it as soon as possible to avoid restrictions."
                )

                if NotificationService.send_email(user.email, "Library Fine Reminder", message):
                    log = NotificationLog(
                        user_id=user.id,
                        message=message,
                        notification_type="fine_reminder"
                    )
                    db.session.add(log)
                    reminders_sent += 1

            db.session.commit()
            return {"message": f"Fine reminders sent to {reminders_sent} users"}, 200  # ✅ JSON-safe dict

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500  # ✅ JSON-safe dict
