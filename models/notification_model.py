from datetime import datetime
from models import db

class NotificationLog(db.Model):
    """Tracks Email Notifications"""
    __tablename__ = "notification_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")

    def __repr__(self):
        return f"<NotificationLog User: {self.user_id}, Type: {self.notification_type}, Sent: {self.sent_at}>"
