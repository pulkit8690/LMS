import logging
from flask import Flask, jsonify
from config import Config
from extensions import db, mail, migrate, socketio, limiter, jwt  # ✅ Import extensions
from flask_cors import CORS
from celery import Celery
from routes import register_routes  # ✅ Removed `backend.`

# ✅ Enable Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize Celery
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

def create_app():
    """Creates and configures the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    # ✅ Fix CORS to Work with Frontend
    CORS(app, supports_credentials=True, 
         resources={r"/*": {"origins": "*"}}, 
         expose_headers=["Authorization", "Content-Type"])  # ✅ Allow frontend to read headers
    
    # ✅ Initialize Celery with Flask Context
    celery.conf.update(app.config)

    # ✅ Import & Register Routes AFTER Extensions
    register_routes(app)

    # ✅ Handle JSON Errors Gracefully
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Invalid request data"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    # ✅ Home Route
    @app.route("/")
    @limiter.limit("10 per second")
    def home():
        logging.info("Home route accessed")
        return jsonify({"message": "Welcome to Library Management System API!"})

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)  # ✅ Required for Flask-SocketIO in Development Mode
