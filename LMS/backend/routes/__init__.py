from backend.routes.auth_routes import auth_bp
from backend.routes.book_routes import book_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.student_routes import student_bp
from backend.routes.reservation_routes import reservation_bp
from backend.routes.payment_routes import payment_bp
from backend.routes.notification_routes import notification_bp


def register_routes(app):
    """Registers all blueprints with unique names to prevent conflicts."""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(book_bp, url_prefix="/books", name_prefix="books_")  # ✅ FIX
    app.register_blueprint(admin_bp, url_prefix="/admin", name_prefix="admin_")  # ✅ FIX
    app.register_blueprint(student_bp, url_prefix="/students", name_prefix="students_")  # ✅ FIX
    app.register_blueprint(reservation_bp, url_prefix="/reservations")
    app.register_blueprint(payment_bp, url_prefix="/payments")
    app.register_blueprint(notification_bp, url_prefix="/notifications")


