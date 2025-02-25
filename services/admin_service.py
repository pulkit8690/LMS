# services/admin_service.py

from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

# Import the single db instance
from models import db

# Import your models
from models.user_model import User
from models.book_model import Book
from models.transaction_model import BorrowedBook
from models.reservation_model import ReservedBook

class AdminService:
    """Service class handling admin operations."""

    @staticmethod
    def block_student(student_id):
        """Blocks a student account."""
        student = User.query.get(student_id)
        if not student or student.role != "user":
            return jsonify({"error": "Student not found"}), 404

        student.is_blocked = True
        db.session.commit()
        return jsonify({"message": "Student blocked successfully"}), 200

    @staticmethod
    def unblock_student(student_id):
        """Unblocks a student account."""
        student = User.query.get(student_id)
        if not student or student.role != "user":
            return jsonify({"error": "Student not found"}), 404

        student.is_blocked = False
        db.session.commit()
        return jsonify({"message": "Student unblocked successfully"}), 200

    @staticmethod
    def issue_book(book_id, student_id):
        """Issues a book to a student."""
        student = User.query.get(student_id)
        book = Book.query.get(book_id)

        if not student or student.role != "user":
            return jsonify({"error": "Student not found"}), 404
        if not book or book.copies_available < 1:
            return jsonify({"error": "Book not available"}), 400

        due_date = datetime.utcnow() + timedelta(days=14)  # 2-week borrow period
        new_borrow = BorrowedBook(
            user_id=student.id,
            book_id=book.id,
            due_date=due_date,
            returned=False
        )

        book.copies_available -= 1
        db.session.add(new_borrow)
        db.session.commit()

        return jsonify({"message": "Book issued successfully",
                        "due_date": due_date.strftime("%Y-%m-%d")}), 200

    @staticmethod
    def accept_return(book_id, student_id):
        """Accepts a book return from a student."""
        borrow_record = BorrowedBook.query.filter_by(
            user_id=student_id,
            book_id=book_id,
            returned=False
        ).first()

        if not borrow_record:
            return jsonify({"error": "No active borrow record found"}), 400

        book = Book.query.get(book_id)
        book.copies_available += 1
        borrow_record.returned = True
        borrow_record.return_date = datetime.utcnow()

        db.session.commit()
        return jsonify({"message": "Book return accepted"}), 200

    @staticmethod
    def approve_extension(book_id, student_id, action):
        """Approves or rejects a book extension request."""
        borrow_record = BorrowedBook.query.filter_by(
            user_id=student_id,
            book_id=book_id,
            returned=False
        ).first()

        if not borrow_record:
            return jsonify({"error": "No active borrow record found"}), 400

        if action == "accept":
            borrow_record.due_date += timedelta(days=7)
            db.session.commit()
            return jsonify({
                "message": "Extension approved",
                "new_due_date": borrow_record.due_date.strftime("%Y-%m-%d")
            }), 200
        elif action == "reject":
            return jsonify({"message": "Extension request rejected"}), 200
        else:
            return jsonify({"error": "Invalid action"}), 400

    @staticmethod
    def delete_book(book_id):
        """Deletes a book and removes associated reservations."""
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        try:
            # Delete all reservations before deleting the book
            ReservedBook.query.filter_by(book_id=book_id).delete()

            db.session.delete(book)
            db.session.commit()
            return jsonify({"message": "Book deleted successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def generate_reports():
        """Generates reports for the library system."""
        try:
            total_books = db.session.query(db.func.count(Book.id)).scalar()
            total_students = db.session.query(db.func.count(User.id)).filter(User.role == "user").scalar()
            borrowed_books = db.session.query(db.func.count(BorrowedBook.id)).filter(BorrowedBook.returned.is_(False)).scalar()

            return jsonify({
                "total_books": total_books,
                "total_students": total_students,
                "borrowed_books": borrowed_books
            }), 200
        except SQLAlchemyError as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
