from datetime import datetime
from models import db

class BorrowedBook(db.Model):
    """Tracks Book Borrowing and Returns"""
    __tablename__ = "borrowed_book"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    due_date = db.Column(db.DateTime, nullable=False)
    returned = db.Column(db.Boolean, default=False)
    return_date = db.Column(db.DateTime, nullable=True)
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)

    def calculate_fine(self):
        """Calculate fine for late return"""
        fine_per_day = 5  # ₹5 per day fine
        if self.return_date and self.return_date > self.due_date:
            self.fine_amount = max(0, (self.return_date - self.due_date).days * fine_per_day)
        else:
            self.fine_amount = 0

    def __repr__(self):
        return f"<BorrowedBook User: {self.user_id}, Book: {self.book_id}, Due: {self.due_date}, Returned: {self.returned}>"

class PaymentRecord(db.Model):
    """Tracks Fine Payments"""
    __tablename__ = "payment_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default="pending")
    transaction_id = db.Column(db.String(255), unique=True, nullable=False)

    user = db.relationship("User", backref="payments")

    def __repr__(self):
        return f"<PaymentRecord User: {self.user_id}, Amount: {self.amount}, Status: {self.payment_status}>"
