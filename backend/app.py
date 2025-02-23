import logging
from flask import Flask, jsonify
from backend.config import Config
from backend.database import db, init_db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery

# ✅ Initialize Flask Extensions
mail = Mail()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")  # ✅ WebSocket CORS Handling
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")

# ✅ Enable Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize Celery
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Initialize Extensions
    init_db(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)  # ✅ Initialize JWT
    mail.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)
    
    # ✅ Fix CORS to Work with Frontend
    CORS(app, supports_credentials=True, 
         resources={r"/*": {"origins": "*"}}, 
         expose_headers=["Authorization", "Content-Type"])  # ✅ Allow frontend to read headers
    
    # ✅ Initialize Celery with Flask Context
    celery.conf.update(app.config)

    # ✅ Handle JSON Errors Gracefully
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Invalid request data"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    # ✅ Import & Register Routes AFTER Extensions
    from backend.routes import register_routes
    register_routes(app)

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
