from datetime import datetime
from models import db

class ReservedBook(db.Model):
    """Tracks Book Reservations"""
    __tablename__ = "reserved_books"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")

    user = db.relationship("User", backref="reservations", lazy=True)
    book = db.relationship("Book", backref="reservations", lazy=True)

    def __repr__(self):
        return f"<ReservedBook User: {self.user_id}, Book: {self.book_id}, Status: {self.status}>"
