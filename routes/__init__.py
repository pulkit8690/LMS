from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.admin_routes import admin_bp
from routes.student_routes import student_bp
from routes.reservation_routes import reservation_bp
from routes.payment_routes import payment_bp
from routes.notification_routes import notification_bp

def register_routes(app):
    """Registers all blueprints with proper URL prefixes."""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(book_bp, url_prefix="/books")  # ✅ Removed `name_prefix`
    app.register_blueprint(admin_bp, url_prefix="/admin")  # ✅ Removed `name_prefix`
    app.register_blueprint(student_bp, url_prefix="/students")  # ✅ Removed `name_prefix`
    app.register_blueprint(reservation_bp, url_prefix="/reservations")
    app.register_blueprint(payment_bp, url_prefix="/payments")
    app.register_blueprint(notification_bp, url_prefix="/notifications")
