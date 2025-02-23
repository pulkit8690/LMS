from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from backend.models import db, Book, Category, User, BorrowedBook, ReservedBook
from flask_socketio import emit
from backend.app import socketio  # Import WebSocket instance
from datetime import datetime

book_bp = Blueprint("books", __name__)

# ✅ Ensure Admin Access
def admin_required(fn):
    """Decorator to ensure the user is an admin."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# ✅ Add Category (Admin Only)
@book_bp.route("/category/add", methods=["POST"])
@admin_required
def add_category():
    """Admin can add a new book category."""
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"error": "Category already exists"}), 400

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({"message": "Category added successfully", "id": new_category.id}), 201


# ✅ Add Book (Admin Only)
@book_bp.route("/add", methods=["POST"])
@admin_required
def add_book():
    """Admin can add a new book to the library."""
    data = request.json

    try:
        title = data.get("title")
        author = data.get("author")
        isbn = data.get("isbn")
        category_id = int(data.get("category_id"))  # ✅ Ensure category_id is an integer
        copies_available = int(data.get("copies_available", 1))  # ✅ Ensure copies_available is an integer

        if not title or not author or not isbn or not category_id:
            return jsonify({"error": "All fields (title, author, isbn, category_id) are required"}), 400

        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            return jsonify({"error": "Book with this ISBN already exists"}), 400

        new_book = Book(title=title, author=author, isbn=isbn, category_id=category_id, copies_available=copies_available)
        db.session.add(new_book)
        db.session.commit()

        return jsonify({"message": "Book added successfully", "id": new_book.id}), 201

    except ValueError:
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()  # ✅ Print full error details in Flask logs
        return jsonify({"error": str(e)}), 500  # ✅ Ensures JSON response


# ✅ View All Books
@book_bp.route("/", methods=["GET"])
def get_books():
    """Fetch all books with their category."""
    books = Book.query.all()
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category_id": book.category_id,
            "category_name": book.category.name,
            "copies_available": book.copies_available,
        }
        for book in books
    ]
    return jsonify(books_list), 200


# ✅ Get Books by Category
@book_bp.route("/category/<int:category_id>", methods=["GET"])
def get_books_by_category(category_id):
    """Fetch books filtered by category."""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    books = Book.query.filter_by(category_id=category_id).all()
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "copies_available": book.copies_available,
        }
        for book in books
    ]
    return jsonify({"category": category.name, "books": books_list}), 200


# ✅ Update a Book (Admin Only)
@book_bp.route("/update/<int:book_id>", methods=["PUT"])
@admin_required
def update_book(book_id):
    """Admin can update book details."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.json
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.isbn = data.get("isbn", book.isbn)
    book.copies_available = data.get("copies_available", book.copies_available)

    new_category_id = data.get("category_id", book.category_id)
    if new_category_id and not Category.query.get(new_category_id):
        return jsonify({"error": "Category not found"}), 404
    book.category_id = new_category_id

    db.session.commit()

    # 🔥 Fixed `emit()` method (removed `broadcast=True`)
    socketio.emit("book_update", {"message": f"Book updated: {book.title}"}, to="all")

    return jsonify({"message": "Book updated successfully"}), 200


@book_bp.route("/delete/<int:book_id>", methods=["DELETE"])
@admin_required
def delete_book(book_id):
    """Admin can delete a book."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # ✅ First, delete all reservations related to this book
    ReservedBook.query.filter_by(book_id=book_id).delete()

    # ✅ Now, delete the book
    db.session.delete(book)
    db.session.commit()

    # 🔥 Emit update (removed `broadcast=True`)
    socketio.emit("book_update", {"message": f"Book deleted: {book.title}"}, to="all")

    return jsonify({"message": "Book deleted successfully"}), 200



# ✅ Borrow Book
@book_bp.route("/borrow", methods=["POST"])
@jwt_required()
def borrow_book():
    """User borrows a book."""
    data = request.json
    user_id = get_jwt_identity()
    book_id = data.get("book_id")

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if book.copies_available < 1:
        return jsonify({"error": "No copies available"}), 400

    borrowed_book = BorrowedBook(user_id=user_id, book_id=book_id, due_date=datetime.utcnow())
    book.copies_available -= 1

    db.session.add(borrowed_book)
    db.session.commit()

    return jsonify({"message": "Book borrowed successfully"}), 200


# ✅ Return Book
@book_bp.route("/return", methods=["POST"])
@jwt_required()
def return_book():
    """User returns a borrowed book."""
    data = request.json
    user_id = get_jwt_identity()
    book_id = data.get("book_id")

    borrowed_book = BorrowedBook.query.filter_by(user_id=user_id, book_id=book_id, returned=False).first()
    if not borrowed_book:
        return jsonify({"error": "Borrowed book not found"}), 404

    borrowed_book.returned = True
    borrowed_book.return_date = datetime.utcnow()

    book = Book.query.get(book_id)
    if book:
        book.copies_available += 1

    db.session.commit()

    return jsonify({"message": "Book returned successfully"}), 200


# ✅ Reserve Book
@book_bp.route("/reserve", methods=["POST"])
@jwt_required()
def reserve_book():
    """User reserves a book."""
    data = request.json
    user_id = get_jwt_identity()
    book_id = data.get("book_id")

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    reserved_book = ReservedBook(user_id=user_id, book_id=book_id)
    db.session.add(reserved_book)
    db.session.commit()

    return jsonify({"message": "Book reserved successfully"}), 200
