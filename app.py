import logging
from flask import Flask, jsonify
from config import Config
from extensions import db, mail, migrate, socketio, limiter, jwt  # ✅ Import SQLAlchemy `db`
from flask_cors import CORS
from celery_config import celery, init_celery
from routes import register_routes  # ✅ Import routes AFTER extensions

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_app():
    """Creates and configures the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Initialize Extensions before importing models
    db.init_app(app)  # ✅ Ensure this is called before using `db`
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    CORS(app, supports_credentials=True, 
         resources={r"/*": {"origins": "*"}}, 
         expose_headers=["Authorization", "Content-Type"])

    # ✅ Initialize Celery (if Redis is enabled)
    if celery:
        init_celery(app)

    # ✅ Import routes AFTER initializing extensions
    register_routes(app)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Invalid request data"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.route("/")
    @limiter.limit("10 per second")
    def home():
        logging.info("Home route accessed")
        return jsonify({"message": "Welcome to Library Management System API!"})

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
