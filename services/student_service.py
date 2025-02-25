# services/student_service.py

from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

# Import the single db instance
from models import db
from models.book_model import Book
from models.transaction_model import BorrowedBook
from services.reservation_service import ReservationService

class StudentService:
    """Service class handling student-related book borrowing and returning operations."""
    FINE_PER_DAY = 5  # ₹5 per day late fine

    @staticmethod
    def borrow_book(user_id, book_id):
        """Allows a student to borrow a book if available."""
        try:
            book = Book.query.get(book_id)
            if not book:
                return jsonify({"error": "Book not found"}), 404

            if book.copies_available < 1:
                return jsonify({"error": "Book is not available for borrowing"}), 400

            # Check if student already borrowed this book
            existing_borrow = BorrowedBook.query.filter_by(
                user_id=user_id,
                book_id=book_id,
                returned=False
            ).first()
            if existing_borrow:
                return jsonify({"error": "You have already borrowed this book"}), 400

            due_date = datetime.utcnow() + timedelta(days=14)
            borrow_entry = BorrowedBook(
                user_id=user_id,
                book_id=book_id,
                due_date=due_date,
                returned=False
            )
            book.copies_available -= 1

            db.session.add(borrow_entry)
            db.session.commit()
            return jsonify({
                "message": "Book borrowed successfully",
                "due_date": due_date.strftime('%Y-%m-%d')
            }), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def get_borrowing_history(user_id):
        """Fetches borrowing history including book names, dates, and fine details."""
        try:
            history = BorrowedBook.query.filter_by(user_id=user_id).order_by(BorrowedBook.borrow_date.desc()).all()
            if not history:
                return jsonify({"message": "No borrowing history found"}), 200

            history_data = []
            for record in history:
                history_data.append({
                    "book_id": record.book.id,
                    "title": record.book.title,
                    "author": record.book.author,
                    "borrow_date": record.borrow_date.strftime("%Y-%m-%d"),
                    "due_date": record.due_date.strftime("%Y-%m-%d"),
                    "return_date": record.return_date.strftime("%Y-%m-%d") if record.return_date else "Not returned",
                    "fine_amount": record.fine_amount if record.fine_amount > 0 else 0,
                    "fine_paid": "Yes" if record.fine_paid else "No",
                    "status": "Returned" if record.returned else "Borrowed"
                })

            return jsonify(history_data), 200

        except SQLAlchemyError as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def return_book(borrow_id):
        """Handles the return of a borrowed book and notifies reserved users."""
        try:
            borrow_entry = BorrowedBook.query.get(borrow_id)
            if not borrow_entry:
                return jsonify({"error": "Borrow record not found"}), 404

            book = Book.query.get(borrow_entry.book_id)
            if not book:
                return jsonify({"error": "Book details not found"}), 404

            borrow_entry.returned = True
            borrow_entry.return_date = datetime.utcnow()
            book.copies_available += 1

            db.session.commit()

            # Notify the first reserved user if any
            reserved_user_id = ReservationService.notify_reservation(book.id)
            if reserved_user_id:
                # Log or handle the notification any way you want
                print(f"📢 Notifying user {reserved_user_id} that '{book.title}' is now available!")

            return jsonify({"message": "Book returned successfully"}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def request_extension(borrow_id):
        """Allows a student to request a 7-day extension for a borrowed book."""
        try:
            borrow_entry = BorrowedBook.query.get(borrow_id)
            if not borrow_entry or borrow_entry.returned:
                return jsonify({"error": "No active borrow record found"}), 400

            borrow_entry.due_date += timedelta(days=7)
            db.session.commit()
            return jsonify({
                "message": "Book extension granted",
                "new_due_date": borrow_entry.due_date.strftime('%Y-%m-%d')
            }), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def get_borrowed_books(user_id):
        """Fetches all books currently borrowed by a student."""
        try:
            borrowed_books = BorrowedBook.query.filter_by(
                user_id=user_id,
                returned=False
            ).all()

            borrowed_data = [
                {
                    "book_id": b.book.id,
                    "title": b.book.title,
                    "author": b.book.author,
                    "due_date": b.due_date.strftime('%Y-%m-%d')
                }
                for b in borrowed_books
            ]

            return jsonify(borrowed_data), 200

        except SQLAlchemyError as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
