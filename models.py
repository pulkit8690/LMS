from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    """User Model: Stores User Information"""
    __tablename__ = "user"
    __table_args__ = (db.Index("idx_email", "email"),)  # ✅ Index for faster lookups

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords
    role = db.Column(db.String(20), default="user")
    is_blocked = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    login_attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Added Timestamp

    # ✅ Relationship to Borrowed Books (Cascade delete if user is deleted)
    borrowed_books = db.relationship("BorrowedBook", backref="user", lazy=True, cascade="all, delete")

    def set_password(self, password):
        """Hash password before saving."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.name} - {self.email}>"

class UserOTP(db.Model):
    """UserOTP Model: Stores OTP for authentication"""
    __tablename__ = "user_otp"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    otp = db.Column(db.String(6), nullable=False)  # OTP length is 6 digits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Added Timestamp

    def __repr__(self):
        return f"<UserOTP {self.email} - {self.otp}>"

class Category(db.Model):
    """Category Model: Stores all book categories"""
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Added Timestamp

    # ✅ Relationship to Books (Cascade delete if category is deleted)
    books = db.relationship("Book", backref="category", lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Category {self.name}>"

class Book(db.Model):
    """Book Model: Stores library books"""
    __tablename__ = "book"
    __table_args__ = (db.Index("idx_isbn", "isbn"),)  # ✅ Index for faster ISBN lookup

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    copies_available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Added Timestamp

    # ✅ Relationship to Borrowed Books (Cascade delete if book is deleted)
    borrowed_books = db.relationship("BorrowedBook", backref="book", lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Book {self.title} - {self.author} - {self.isbn}>"

class BorrowedBook(db.Model):
    """Tracks Book Borrowing and Returns"""
    __tablename__ = "borrowed_book"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=db.func.current_timestamp())  # ✅ Borrow date
    due_date = db.Column(db.DateTime, nullable=False)
    returned = db.Column(db.Boolean, default=False)  # ✅ True if returned
    return_date = db.Column(db.DateTime, nullable=True)  # ✅ Stores actual return date if returned
    fine_amount = db.Column(db.Float, default=0.0)  # ✅ Fine (if any)
    fine_paid = db.Column(db.Boolean, default=False)  # ✅ If fine was paid
def __repr__(self):
        return f"<BorrowedBook User: {self.user_id}, Book: {self.book_id}, Due: {self.due_date}, Returned: {self.returned}>"

class ReservedBook(db.Model):
    """Tracks book reservations when all copies are borrowed."""
    __tablename__ = "reserved_books"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")  # pending, notified, cancelled

    user = db.relationship("User", backref="reservations")
    book = db.relationship("Book", backref="reservations")

    def __repr__(self):
        return f"<ReservedBook User: {self.user_id}, Book: {self.book_id}, Status: {self.status}>"


    def calculate_fine(self):
        """Calculate fine based on return date."""
        fine_per_day = 5  # ₹5 per day fine
        if self.return_date and self.return_date > self.due_date:
            self.fine_amount = max(0, (self.return_date - self.due_date).days * fine_per_day)
        else:
            self.fine_amount = 0

    
class PaymentRecord(db.Model):
    """Tracks fine payments for students."""
    __tablename__ = "payment_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default="pending")  # pending, completed, failed
    transaction_id = db.Column(db.String(255), unique=True, nullable=False)
    razorpay_payment_id = db.Column(db.String(255), unique=True, nullable=True)

    user = db.relationship("User", backref="payments")

    def __repr__(self):
        return f"<PaymentRecord User: {self.user_id}, Amount: {self.amount}, Status: {self.payment_status}>"
    
class NotificationLog(db.Model):
    """Tracks email notifications sent to students."""
    __tablename__ = "notification_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # due_date, fine_reminder
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")

    def __repr__(self):
        return f"<NotificationLog User: {self.user_id}, Type: {self.notification_type}, Sent: {self.sent_at}>"


