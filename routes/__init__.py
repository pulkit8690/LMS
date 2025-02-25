# routes/__init__.py

import logging
from flask import Flask

# Import all blueprint objects
try:
    from routes.auth_routes import auth_bp
    from routes.book_routes import book_bp
    from routes.admin_routes import admin_bp
    from routes.student_routes import student_bp
    from routes.reservation_routes import reservation_bp
    from routes.payment_routes import payment_bp
    from routes.notification_routes import notification_bp
except ImportError as e:
    logging.error(f"❌ Route Import Error: {e}")
    raise  # Stop execution if routes fail to import


def register_routes(app: Flask):
    """Registers all blueprints with proper URL prefixes."""
    app.register_blueprint(auth_bp, url_prefix="/auth")          # Authentication
    app.register_blueprint(book_bp, url_prefix="/books")         # Book Management
    app.register_blueprint(admin_bp, url_prefix="/admin")        # Admin Panel
    app.register_blueprint(student_bp, url_prefix="/students")   # Student Actions
    app.register_blueprint(reservation_bp, url_prefix="/reservations")  # Reservations
    app.register_blueprint(payment_bp, url_prefix="/payments")   # Payment/Fines
    app.register_blueprint(notification_bp, url_prefix="/notifications")  # Notifications & Alerts

    logging.info("✅ All routes registered successfully!")
