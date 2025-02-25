# routes/student_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import exists

# Import the single db instance and models
from models import db
from models.user_model import User
from models.book_model import Book
from models.transaction_model import BorrowedBook

student_bp = Blueprint("student", __name__)

# ✅ Get All Available Books
@student_bp.route("/books", methods=["GET"])
@jwt_required()
def get_books():
    books = Book.query.all()
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category": book.category.name if book.category else "Unknown",
            "copies_available": book.copies_available
        }
        for book in books
    ]
    return jsonify(books_list), 200

# ✅ Borrow a Book (Only If No Pending Fines)
@student_bp.route("/books/borrow/<int:book_id>", methods=["POST"])
@jwt_required()
def borrow_book(book_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    book = Book.query.get(book_id)

    if not book or book.copies_available < 1:
        return jsonify({"error": "Book not available"}), 400

    # Check for unpaid fines
    pending_fines = db.session.query(
        exists().where(
            BorrowedBook.user_id == user_id,
            BorrowedBook.fine_amount > 0,
            BorrowedBook.fine_paid.is_(False)
        )
    ).scalar()

    if pending_fines:
        return jsonify({"error": "You have unpaid fines. Pay them before borrowing another book."}), 403

    # Borrow limit check (max 3 books)
    MAX_BORROW_LIMIT = 3
    current_borrow_count = BorrowedBook.query.filter_by(user_id=user.id, returned=False).count()
    if current_borrow_count >= MAX_BORROW_LIMIT:
        return jsonify({"error": "Borrow limit reached (Max: 3 books)"}), 400

    due_date = datetime.utcnow() + timedelta(days=14)
    new_borrow = BorrowedBook(
        user_id=user.id,
        book_id=book.id,
        due_date=due_date,
        returned=False,
        fine_paid=False
    )

    book.copies_available -= 1
    db.session.add(new_borrow)
    db.session.commit()

    return jsonify({"message": "Book borrowed successfully", "due_date": due_date.strftime("%Y-%m-%d")}), 200

# ✅ Return a Book
@student_bp.route("/books/return/<int:borrow_id>", methods=["POST"])
@jwt_required()
def return_book(borrow_id):
    user_id = get_jwt_identity()
    borrow_record = BorrowedBook.query.filter_by(
        id=borrow_id,
        user_id=user_id,
        returned=False
    ).first()

    if not borrow_record:
        return jsonify({"error": "No active borrow record found"}), 400

    fine_amount = 0
    fine_per_day = 5  # ₹5 per day fine
    if borrow_record.due_date < datetime.utcnow():
        days_late = (datetime.utcnow() - borrow_record.due_date).days
        fine_amount = days_late * fine_per_day

    book = Book.query.get(borrow_record.book_id)
    if book:
        book.copies_available += 1

    borrow_record.returned = True
    borrow_record.return_date = datetime.utcnow()
    borrow_record.fine_amount = fine_amount
    borrow_record.fine_paid = False

    db.session.commit()

    return jsonify({"message": "Book returned successfully", "fine_amount": fine_amount}), 200

# ✅ Pay Fine
@student_bp.route("/books/pay-fine", methods=["POST"])
@jwt_required()
def pay_fine():
    user_id = get_jwt_identity()
    pending_fines = BorrowedBook.query.filter(
        BorrowedBook.user_id == user_id,
        BorrowedBook.fine_amount > 0,
        BorrowedBook.fine_paid.is_(False)
    ).all()

    if not pending_fines:
        return jsonify({"message": "No pending fines to pay."}), 200

    for fine in pending_fines:
        fine.fine_paid = True

    db.session.commit()
    return jsonify({"message": "All pending fines have been paid."}), 200

# ✅ View Borrowed Books
@student_bp.route("/books/borrowed", methods=["GET"])
@jwt_required()
def view_borrowed_books():
    user_id = get_jwt_identity()
    borrowed_books = BorrowedBook.query.filter_by(user_id=user_id, returned=False).all()

    books_list = [
        {
            "id": record.book.id,
            "title": record.book.title,
            "author": record.book.author,
            "due_date": record.due_date.strftime("%Y-%m-%d"),
            "fine_due": record.fine_amount if record.fine_amount else 0
        }
        for record in borrowed_books
    ]

    return jsonify(books_list), 200

# ✅ Request Book Extension
@student_bp.route("/books/extend/<int:book_id>", methods=["POST"])
@jwt_required()
def request_extension(book_id):
    user_id = get_jwt_identity()
    borrow_record = BorrowedBook.query.filter_by(user_id=user_id, book_id=book_id, returned=False).first()

    if not borrow_record:
        return jsonify({"error": "No active borrow record found"}), 400

    borrow_record.due_date += timedelta(days=7)
    db.session.commit()

    return jsonify({"message": "Due date extended successfully", "new_due_date": borrow_record.due_date.strftime('%Y-%m-%d')}), 200

# ✅ Edit Profile (Password Change Only)
@student_bp.route("/profile/edit", methods=["PUT"])
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    password = data.get("password")

    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    user.password = generate_password_hash(password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
