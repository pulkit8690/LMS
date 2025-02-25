from flask_migrate import Migrate
from extensions import db

migrate = Migrate()

def init_migrate(app):
    """Initialize Flask-Migrate with the single db instance."""
    migrate.init_app(app, db)
