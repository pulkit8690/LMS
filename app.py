# app.py

import sys
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Import your Config class from config.py (same folder)
from config import Config

# Import your extension init function
from extensions import init_extensions

def create_app():
    """
    Factory function that creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(Config)  # Load settings from config.py

    # 1) Initialize all Flask extensions
    init_extensions(app)

    # 2) Register your routes/blueprints
    with app.app_context():
        from routes import register_routes  # or adapt if your route file is elsewhere
        register_routes(app)

    # 3) Define error handlers
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.error(f"400 Error: {error}")
        return jsonify({"error": "Invalid request data"}), 400

    @app.errorhandler(404)
    def not_found(error):
        app.logger.error(f"404 Error: {error}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    # 4) Simple Home Route
    @app.route("/")
    def home():
        app.logger.info("Home route accessed")
        return jsonify({"message": "Welcome to Library Management System API!"})

    # 5) Enable CORS
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": "*"}},
        expose_headers=["Authorization", "Content-Type"],
    )

    return app
