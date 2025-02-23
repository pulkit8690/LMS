from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta, datetime
from models import User, db, Book, BorrowedBook, ReservedBook  # ✅ Removed `backend.`
from sqlalchemy.exc import SQLAlchemyError


class AuthService:
    """Service class handling user authentication and registration."""

    @staticmethod
    def register_user(name, email, password, role="user"):
        """Registers a new user in the system."""
        if not name or not email or not password:
            return {"error": "All fields are required"}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"error": "Email already exists"}, 400

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201

    @staticmethod
    def authenticate_user(email, password):
        """Authenticates a user and generates an access token."""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return {"error": "Invalid credentials"}, 401
        
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {"access_token": access_token, "refresh_token": refresh_token}, 200

    @staticmethod
    def refresh_access_token(identity):
        """Generates a new access token using a refresh token."""
        access_token = create_access_token(identity=identity, expires_delta=timedelta(days=1))
        return {"access_token": access_token}, 200

    @staticmethod
    def get_user_profile(user_id):
        """Fetches user profile details."""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }, 200


class AdminService:
    """Service class handling admin operations."""

    @staticmethod
    def block_student(student_id):
        """Blocks a student account."""
        student = User.query.get(student_id)
        if not student or student.role != "user":
            return {"error": "Student not found"}, 404

        student.is_blocked = True
        db.session.commit()
        return {"message": "Student blocked successfully"}, 200

    @staticmethod
    def unblock_student(student_id):
        """Unblocks a student account."""
        student = User.query.get(student_id)
        if not student or student.role != "user":
            return {"error": "Student not found"}, 404

        student.is_blocked = False
        db.session.commit()
        return {"message": "Student unblocked successfully"}, 200

    @staticmethod
    def issue_book(book_id, student_id):
        """Issues a book to a student."""
        student = User.query.get(student_id)
        book = Book.query.get(book_id)

        if not student or student.role != "user":
            return {"error": "Student not found"}, 404
        if not book or book.copies_available < 1:
            return {"error": "Book not available"}, 400

        due_date = datetime.utcnow() + timedelta(days=14)  # 2-week borrow period
        new_borrow = BorrowedBook(user_id=student.id, book_id=book.id, due_date=due_date, returned=False)

        book.copies_available -= 1
        db.session.add(new_borrow)
        db.session.commit()

        return {"message": "Book issued successfully", "due_date": due_date.strftime("%Y-%m-%d")}, 200

    @staticmethod
    def accept_return(book_id, student_id):
        """Accepts a book return from a student."""
        borrow_record = BorrowedBook.query.filter_by(user_id=student_id, book_id=book_id, returned=False).first()

        if not borrow_record:
            return {"error": "No active borrow record found"}, 400

        book = Book.query.get(book_id)
        book.copies_available += 1
        borrow_record.returned = True
        borrow_record.return_date = datetime.utcnow()

        db.session.commit()
        return {"message": "Book return accepted"}, 200

    @staticmethod
    def approve_extension(book_id, student_id, action):
        """Approves or rejects a book extension request."""
        borrow_record = BorrowedBook.query.filter_by(user_id=student_id, book_id=book_id, returned=False).first()

        if not borrow_record:
            return {"error": "No active borrow record found"}, 400

        if action == "accept":
            borrow_record.due_date += timedelta(days=7)
            db.session.commit()
            return {"message": "Extension approved", "new_due_date": borrow_record.due_date.strftime("%Y-%m-%d")}, 200
        elif action == "reject":
            return {"message": "Extension request rejected"}, 200
        else:
            return {"error": "Invalid action"}, 400

    @staticmethod
    def delete_book(book_id):
        """Deletes a book and removes associated reservations."""
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Book not found"}, 404

        # Delete all reservations before deleting the book
        ReservedBook.query.filter_by(book_id=book_id).delete()

        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted successfully"}, 200

    @staticmethod
    def generate_reports():
        """Generates reports for the library system."""
        total_books = db.session.query(db.func.count(Book.id)).scalar()
        total_students = db.session.query(db.func.count(User.id)).filter(User.role == "user").scalar()
        borrowed_books = db.session.query(db.func.count(BorrowedBook.id)).filter(BorrowedBook.returned == False).scalar()

        return {
            "total_books": total_books,
            "total_students": total_students,
            "borrowed_books": borrowed_books
        }, 200
