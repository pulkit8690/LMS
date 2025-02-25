from datetime import datetime
from models import db

class Category(db.Model):
    """Stores Book Categories"""
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relationship to Books
    books = db.relationship("Book", backref="category", lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Category {self.name}>"

class Book(db.Model):
    """Stores Library Books"""
    __tablename__ = "book"
    __table_args__ = (db.Index("idx_isbn", "isbn"),)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    copies_available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relationship to Borrowed Books
    borrowed_books = db.relationship("BorrowedBook", backref="book", lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Book {self.title} - {self.author} - {self.isbn}>"
