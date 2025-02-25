# services/reservation_service.py

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask_mail import Message
from flask import jsonify

# Import the single db instance
from models import db
from extensions import mail
from models.book_model import Book
from models.transaction_model import BorrowedBook
from models.reservation_model import ReservedBook

class ReservationService:
    """Service to handle book reservations."""

    @staticmethod
    def reserve_book(user_id, book_id):
        """Allows a student to reserve a book if no copies are available."""
        try:
            book = Book.query.get(book_id)
            if not book:
                return jsonify({"error": "Book not found"}), 404

            if book.copies_available > 0:
                return jsonify({"error": "Book is available. No need to reserve."}), 400

            existing_reservation = ReservedBook.query.filter_by(
                user_id=user_id,
                book_id=book_id,
                status="pending"
            ).first()
            if existing_reservation:
                return jsonify({"error": "You have already reserved this book"}), 400

            new_reservation = ReservedBook(user_id=user_id, book_id=book_id)
            db.session.add(new_reservation)
            db.session.commit()

            return jsonify({"message": "Book reserved successfully"}), 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def cancel_reservation(user_id, book_id):
        """Allows a student to cancel their reservation."""
        try:
            reservation = ReservedBook.query.filter_by(
                user_id=user_id,
                book_id=book_id,
                status="pending"
            ).first()
            if not reservation:
                return jsonify({"error": "No active reservation found"}), 404

            db.session.delete(reservation)
            db.session.commit()

            return jsonify({"message": "Reservation canceled successfully"}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def notify_reservation(book_id):
        """
        Notifies the first student in the queue when a book is returned.
        Returns the user_id if someone was notified, or None if no reservations.
        """
        try:
            reservation = ReservedBook.query.filter_by(
                book_id=book_id,
                status="pending"
            ).order_by(ReservedBook.reserved_at).first()

            if reservation:
                reservation.status = "notified"
                db.session.commit()

                # Send an email notification
                user_email = reservation.user.email
                msg = Message("Book Available!", recipients=[user_email])
                msg.body = f"The book '{reservation.book.title}' is now available for borrowing!"

                try:
                    mail.send(msg)
                except Exception as e:
                    print(f"❌ Email sending failed: {e}")
                    return jsonify({"error": "Email notification failed, but reservation updated"}), 500

                # Return the user who was notified
                return reservation.user_id

            return None  # No reservations

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
