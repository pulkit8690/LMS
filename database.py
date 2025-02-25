import logging
from sqlalchemy import inspect

# Import the single db instance from extensions
from extensions import db

def init_db(app):
    """
    (Optional) Initializes the database with the given Flask app.
    Typically, you rely on 'flask db migrate/upgrade' with Flask-Migrate.
    If you're in dev mode and want to create tables quickly without migrations:
    
        with app.app_context():
            db.create_all()
    
    Then remove or comment out if using migrations in production.
    """
    try:
        with app.app_context():
            # Optional: check if tables exist, create them (for quick dev only)
            inspector = inspect(db.engine)
            if not inspector.has_table("user"):
                db.create_all()
                print("✅ Tables created successfully (Render Fix)")
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")

def get_db():
    """Returns the database instance."""
    return db
