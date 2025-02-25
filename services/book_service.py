# services/book_service.py

from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

# Import the single db instance
from models import db
from models.book_model import Book, Category

class BookService:
    """Service class handling book-related operations."""

    @staticmethod
    def add_book(title, author, isbn, category_id, copies_available):
        """Adds a new book to the library."""
        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            return {"error": "Book with this ISBN already exists"}, 400

        category = Category.query.get(category_id)
        if not category:
            return {"error": "Category not found"}, 404

        try:
            new_book = Book(
                title=title,
                author=author,
                isbn=isbn,
                category_id=category_id,
                copies_available=copies_available
            )
            db.session.add(new_book)
            db.session.commit()

            return {"message": "Book added successfully", "id": new_book.id}, 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR in add_book(): {str(e)}")  # ✅ Logs exact error
            return {"error": "Database error", "details": str(e)}, 500


    @staticmethod
    def get_books():
        """Fetches all books in the library."""
        books = Book.query.all()
        return jsonify([
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "category_id": book.category_id,
                "copies_available": book.copies_available
            }
            for book in books
        ]), 200

    @staticmethod
    def get_book_by_id(book_id):
        """Fetches details of a single book by ID."""
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category_id": book.category_id,
            "copies_available": book.copies_available
        }), 200

    @staticmethod
    def update_book(book_id, title, author, isbn, category_id, copies_available):
        """Updates a book's details in the library."""
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        book.title = title
        book.author = author
        book.isbn = isbn
        book.category_id = category_id
        book.copies_available = copies_available

        try:
            db.session.commit()
            return jsonify({"message": "Book updated successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def delete_book(book_id):
        """Deletes a book from the library."""
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        try:
            db.session.delete(book)
            db.session.commit()
            return jsonify({"message": "Book deleted successfully"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def search_books(query):
        """Search books by title, author, or ISBN."""
        books = Book.query.filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%")) |
            (Book.isbn.ilike(f"%{query}%"))
        ).all()

        return jsonify([
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "copies_available": book.copies_available
            }
            for book in books
        ]), 200
