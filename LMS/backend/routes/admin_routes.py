from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from sqlalchemy import func
from backend.models import db, User, Book, BorrowedBook, ReservedBook
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)

# ✅ Role-Based Access Control (RBAC) for Admin
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

# ✅ Get All Books
@admin_bp.route("/books", methods=["GET"])
@admin_required
def get_books():
    books = Book.query.all()
    books_list = [{"id": book.id, "title": book.title, "author": book.author, "isbn": book.isbn, 
                   "category_id": book.category_id, "copies_available": book.copies_available} 
                  for book in books]
    return jsonify(books_list), 200

# ✅ Add a Book (Prevent Duplicate ISBN)
@admin_bp.route("/books/add", methods=["POST"])
@admin_required
def add_book():
    data = request.json
    title = data.get("title")
    author = data.get("author")
    isbn = data.get("isbn")
    category_id = data.get("category_id")
    copies_available = data.get("copies_available", 1)

    if not title or not author or not isbn or not category_id:
        return jsonify({"error": "All fields are required"}), 400

    existing_book = Book.query.filter_by(isbn=isbn).first()
    if existing_book:
        return jsonify({"error": "Book with this ISBN already exists"}), 400

    new_book = Book(title=title, author=author, isbn=isbn, category_id=category_id, copies_available=copies_available)
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book added successfully"}), 201

# ✅ Update a Book
@admin_bp.route("/books/update/<int:book_id>", methods=["PUT"])
@admin_required
def update_book(book_id):
    data = request.json
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.isbn = data.get("isbn", book.isbn)
    book.category_id = data.get("category_id", book.category_id)
    book.copies_available = data.get("copies_available", book.copies_available)

    db.session.commit()
    return jsonify({"message": "Book updated successfully"}), 200

# ✅ Delete a Book (Ensure Reserved Books Are Deleted First)
@admin_bp.route("/books/delete/<int:book_id>", methods=["DELETE"])
@admin_required
def delete_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    # ✅ Delete all reservations before deleting the book
    ReservedBook.query.filter_by(book_id=book_id).delete()

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200

# ✅ Get All Students
@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_students():
    students = User.query.filter_by(role="user").all()
    students_list = [{"id": student.id, "name": student.name, "email": student.email, "status": "Blocked" if student.is_blocked else "Active"} for student in students]
    return jsonify(students_list), 200

# ✅ Block/Unblock Student
@admin_bp.route("/students/block/<int:student_id>", methods=["PUT"])
@admin_required
def block_unblock_student(student_id):
    student = User.query.get(student_id)

    if not student or student.role != "user":
        return jsonify({"error": "Student not found"}), 404

    student.is_blocked = not student.is_blocked
    db.session.commit()

    return jsonify({"message": f"Student {'Blocked' if student.is_blocked else 'Unblocked'} successfully"}), 200

# ✅ Issue a Book to Student
@admin_bp.route("/books/issue", methods=["POST"])
@admin_required
def issue_book():
    data = request.json
    book_id = data.get("book_id")
    student_id = data.get("student_id")

    student = User.query.get(student_id)
    book = Book.query.get(book_id)

    if not student or student.role != "user":
        return jsonify({"error": "Student not found"}), 404
    if not book or book.copies_available < 1:
        return jsonify({"error": "Book not available"}), 400

    due_date = datetime.utcnow() + timedelta(days=14)  # 2-week borrow period
    new_borrow = BorrowedBook(user_id=student.id, book_id=book.id, due_date=due_date, returned=False)

    book.copies_available -= 1
    db.session.add(new_borrow)
    db.session.commit()

    return jsonify({"message": "Book issued successfully", "due_date": due_date.strftime("%Y-%m-%d")}), 200

# ✅ Accept Book Return
@admin_bp.route("/books/return", methods=["POST"])
@admin_required
def accept_return():
    data = request.json
    book_id = data.get("book_id")
    student_id = data.get("student_id")

    borrow_record = BorrowedBook.query.filter_by(user_id=student_id, book_id=book_id, returned=False).first()

    if not borrow_record:
        return jsonify({"error": "No active borrow record found"}), 400

    book = Book.query.get(book_id)
    book.copies_available += 1
    borrow_record.returned = True
    borrow_record.return_date = datetime.utcnow()

    db.session.commit()
    return jsonify({"message": "Book return accepted"}), 200

# ✅ View Borrowed Books
@admin_bp.route("/books/borrowed", methods=["GET"])
@admin_required
def view_borrowed_books():
    borrowed_books = BorrowedBook.query.filter_by(returned=False).all()

    books_list = [{"student_id": book.user.id, "student_name": book.user.name, "book_id": book.book.id, "book_title": book.book.title, "due_date": book.due_date.strftime("%Y-%m-%d")} for book in borrowed_books]

    return jsonify(books_list), 200

# ✅ Approve/Reject Book Extension
@admin_bp.route("/books/extend", methods=["PUT"])
@admin_required
def manage_extension():
    data = request.json
    book_id = data.get("book_id")
    student_id = data.get("student_id")
    action = data.get("action")

    borrow_record = BorrowedBook.query.filter_by(user_id=student_id, book_id=book_id, returned=False).first()

    if not borrow_record:
        return jsonify({"error": "No active borrow record found"}), 400

    if action == "accept":
        borrow_record.due_date += timedelta(days=7)
        db.session.commit()
        return jsonify({"message": "Extension approved", "new_due_date": borrow_record.due_date.strftime("%Y-%m-%d")}), 200
    elif action == "reject":
        return jsonify({"message": "Extension request rejected"}), 200
    else:
        return jsonify({"error": "Invalid action"}), 400

# ✅ Generate Reports
@admin_bp.route("/reports", methods=["GET"])
@admin_required
def generate_reports():
    total_books = db.session.query(func.count(Book.id)).scalar()
    total_students = db.session.query(func.count(User.id)).filter(User.role == "user").scalar()
    borrowed_books = db.session.query(func.count(BorrowedBook.id)).filter(BorrowedBook.returned == False).scalar()

    return jsonify({
        "total_books": total_books,
        "total_students": total_students,
        "borrowed_books": borrowed_books
    }), 200
