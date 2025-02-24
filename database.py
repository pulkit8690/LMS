from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import logging

db = SQLAlchemy()

def init_db(app):
    """Initializes the database with the given Flask app."""
    db.init_app(app)

    try:
        with app.app_context():
            inspector = inspect(db.engine)
            if not inspector.has_table("user"):  # ✅ Corrected table existence check
                db.create_all()
                print("✅ Tables created successfully (Render Fix)")
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")

def get_db():
    """Returns the database instance."""
    return db
