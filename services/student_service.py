from models import db, Book, BorrowedBook  # ✅ Removed `backend.`
from datetime import datetime, timedelta
from services.reservation_service import ReservationService  # ✅ Removed `backend.`

class StudentService:
    """Service class handling student-related book borrowing and returning operations."""

    FINE_PER_DAY = 5  # ₹5 per day late fine

    @staticmethod
    def borrow_book(user_id, book_id):
        """Allows a student to borrow a book if available."""
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Book not found"}, 404

        if book.copies_available < 1:
            return {"error": "Book is not available for borrowing"}, 400

        # Check if student has already borrowed the same book
        existing_borrow = BorrowedBook.query.filter_by(user_id=user_id, book_id=book_id, returned=False).first()
        if existing_borrow:
            return {"error": "You have already borrowed this book"}, 400

        due_date = datetime.utcnow() + timedelta(days=14)  # 2-week borrowing period
        borrow_entry = BorrowedBook(user_id=user_id, book_id=book_id, due_date=due_date, returned=False)
        book.copies_available -= 1  # Securely decrement book copies

        db.session.add(borrow_entry)
        db.session.commit()
        return {"message": "Book borrowed successfully", "due_date": due_date.strftime('%Y-%m-%d')}, 201

    @staticmethod
    def get_borrowing_history(user_id):
        """Fetches borrowing history including book names, dates, and fine details."""
        history = BorrowedBook.query.filter_by(user_id=user_id).order_by(BorrowedBook.borrow_date.desc()).all()

        if not history:
            return {"message": "No borrowing history found"}, 200

        history_data = [{
            "book_id": record.book.id,
            "title": record.book.title,
            "author": record.book.author,
            "borrow_date": record.borrow_date.strftime("%Y-%m-%d"),
            "due_date": record.due_date.strftime("%Y-%m-%d"),
            "return_date": record.return_date.strftime("%Y-%m-%d") if record.return_date else "Not returned",
            "fine_amount": record.fine_amount if record.fine_amount > 0 else 0,
            "fine_paid": "Yes" if record.fine_paid else "No",
            "status": "Returned" if record.returned else "Borrowed"
        } for record in history]

        return history_data, 200

    @staticmethod
    def return_book(borrow_id):
        """Handles the return of a borrowed book and notifies reserved users."""
        borrow_entry = BorrowedBook.query.get(borrow_id)
        if not borrow_entry:
            return {"error": "Borrow record not found"}, 404

        book = Book.query.get(borrow_entry.book_id)
        if not book:
            return {"error": "Book details not found"}, 404

        borrow_entry.returned = True
        borrow_entry.return_date = datetime.utcnow()
        book.copies_available += 1  # Securely increment book copies

        db.session.commit()

        # ✅ Check and notify first reserved user
        reserved_user_id = ReservationService.notify_reservation(book.id)
        if reserved_user_id:
            # Send an email/WebSocket notification
            print(f"📢 Notifying user {reserved_user_id} that '{book.title}' is now available!")

        return {"message": "Book returned successfully"}, 200

    @staticmethod
    def request_extension(borrow_id):
        """Allows a student to request a 7-day extension for a borrowed book."""
        borrow_entry = BorrowedBook.query.get(borrow_id)
        if not borrow_entry or borrow_entry.returned:
            return {"error": "No active borrow record found"}, 400

        borrow_entry.due_date += timedelta(days=7)
        db.session.commit()
        return {"message": "Book extension granted", "new_due_date": borrow_entry.due_date.strftime('%Y-%m-%d')}, 200

    @staticmethod
    def get_borrowed_books(user_id):
        """Fetches all books currently borrowed by a student."""
        borrowed_books = BorrowedBook.query.filter_by(user_id=user_id, returned=False).all()

        return [{
            "book_id": borrow.book.id,
            "title": borrow.book.title,
            "author": borrow.book.author,
            "due_date": borrow.due_date.strftime('%Y-%m-%d')
        } for borrow in borrowed_books], 200
