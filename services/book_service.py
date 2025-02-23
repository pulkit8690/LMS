from models import Book, Category, db  # ✅ Removed `backend.`

class BookService:
    """Service class handling book-related operations."""

    @staticmethod
    def add_book(title, author, isbn, category_id, copies_available):
        """Adds a new book to the library (Prevents duplicate ISBNs)."""

        # Check for duplicate ISBN
        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            return {"error": "Book with this ISBN already exists"}, 400

        # Validate category existence
        category = Category.query.get(category_id)
        if not category:
            return {"error": "Category not found"}, 404

        try:
            # Insert new book
            new_book = Book(title=title, author=author, isbn=isbn, category_id=category_id, copies_available=copies_available)
            db.session.add(new_book)
            db.session.commit()
            return {"message": "Book added successfully", "id": new_book.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, 500

    @staticmethod
    def get_books():
        """Fetches all books in the library."""
        books = Book.query.all()
        return [{
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "genre": book.genre,
            "copies_available": book.copies_available
        } for book in books], 200

    @staticmethod
    def get_book_by_id(book_id):
        """Fetches details of a single book by ID."""
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Book not found"}, 404
        
        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "genre": book.genre,
            "copies_available": book.copies_available
        }, 200

    @staticmethod
    def update_book(book_id, title, author, isbn, genre, copies_available):
        """Updates a book's details in the library."""
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Book not found"}, 404
        
        book.title = title
        book.author = author
        book.isbn = isbn
        book.genre = genre
        book.copies_available = copies_available
        db.session.commit()
        return {"message": "Book updated successfully"}, 200

    @staticmethod
    def delete_book(book_id):
        """Deletes a book from the library."""
        book = Book.query.get(book_id)
        if not book:
            return {"error": "Book not found"}, 404
        
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted successfully"}, 200
    
    @staticmethod
    def search_books(query):
        """Search books by title, author, or ISBN."""
        books = Book.query.filter(
            (Book.title.ilike(f"%{query}%")) | 
            (Book.author.ilike(f"%{query}%")) |
            (Book.isbn.ilike(f"%{query}%"))
        ).all()

        return [{
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "copies_available": book.copies_available
        } for book in books], 200
