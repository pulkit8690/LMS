# models/__init__.py

# 1. Import the single db instance from extensions
from extensions import db

# 2. Import all model classes
from models.user_model import User, UserOTP
from models.book_model import Category, Book
from models.transaction_model import BorrowedBook, PaymentRecord
from models.reservation_model import ReservedBook
from models.notification_model import NotificationLog

# That's it! No new db = SQLAlchemy() here.
