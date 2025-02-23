from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initializes the database with the given Flask app."""
    db.init_app(app)

    # ✅ Auto-create tables only in local development (Avoids issues in production with migrations)
    if app.config.get("DEBUG"):  
        with app.app_context():
            db.create_all()

def get_db():
    """Returns the database instance."""
    return db
