from flask_sqlalchemy import SQLAlchemy
import logging

db = SQLAlchemy()

def init_db(app):
    """Initializes the database with the given Flask app."""
    db.init_app(app)

    try:
        with app.app_context():
            # ✅ If running locally, auto-create tables
            if app.config.get("DEBUG"):
                db.create_all()
                print("✅ Tables created successfully (Local Development Mode)")

            # ✅ If running on Render, only create tables if none exist
            elif not db.engine.table_names():
                db.create_all()
                print("✅ Tables created successfully (Render Fix)")
                
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")

def get_db():
    """Returns the database instance."""
    return db
