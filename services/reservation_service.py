from models import db, ReservedBook, Book, BorrowedBook  # ✅ Removed `backend.`
from datetime import datetime
from app import mail  # ✅ Removed `backend.`
from flask_mail import Message

class ReservationService:
    """Service to handle book reservations"""

    @staticmethod
    def reserve_book(user_id, book_id):
        """Allows a student to reserve a book if no copies are available."""
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Book not found"}, 404

        if book.copies_available > 0:
            return {"error": "Book is available. No need to reserve."}, 400

        existing_reservation = ReservedBook.query.filter_by(user_id=user_id, book_id=book_id, status="pending").first()
        if existing_reservation:
            return {"error": "You have already reserved this book"}, 400

        new_reservation = ReservedBook(user_id=user_id, book_id=book_id)
        db.session.add(new_reservation)
        db.session.commit()

        return {"message": "Book reserved successfully"}, 201

    @staticmethod
    def cancel_reservation(user_id, book_id):
        """Allows a student to cancel their reservation."""
        reservation = ReservedBook.query.filter_by(user_id=user_id, book_id=book_id, status="pending").first()
        if not reservation:
            return {"error": "No active reservation found"}, 404

        db.session.delete(reservation)
        db.session.commit()

        return {"message": "Reservation canceled successfully"}, 200

    @staticmethod
    def notify_reservation(book_id):
        """Notifies the first student in the queue when a book is returned."""
        reservation = ReservedBook.query.filter_by(book_id=book_id, status="pending").order_by(ReservedBook.reserved_at).first()

        if reservation:
            reservation.status = "notified"
            db.session.commit()

            # ✅ Send an email notification
            user_email = reservation.user.email
            msg = Message("Book Available!", recipients=[user_email])
            msg.body = f"The book '{reservation.book.title}' is now available for borrowing!"
            mail.send(msg)

            return reservation.user_id  # Return user ID for logging

        return None  # No reservations found
