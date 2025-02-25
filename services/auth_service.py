# services/auth_service.py

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

# Import the single db instance
from models import db
from models.user_model import User


class AuthService:
    """Service class handling user authentication and registration."""

    @staticmethod
    def register_user(name, email, password, role="user"):
        """Registers a new user in the system."""
        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already exists"}), 400

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(name=name, email=email, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "User registered successfully"}), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500

    @staticmethod
    def authenticate_user(email, password):
        """Authenticates a user and generates an access token."""
        user = User.query.filter_by(email=email).first()
        if not user:
            print("❌ User not found!")
            return jsonify({"error": "Invalid credentials"}), 401
        # Store both ID and role in the JWT identity if desired
        print(f"🔍 Stored Hash: {user.password}")
        print(f"🔍 Entered Password: {password}")

        if not check_password_hash(user.password, password):
            print("❌ Password mismatch!")
            return jsonify({"error": "Invalid credentials"}), 401
        print("✅ Password matched!")

        access_token = create_access_token(
            identity={"id": user.id, "role": user.role},
            expires_delta=timedelta(days=1)
        )
        refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role})

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    @staticmethod
    def get_user_profile(user_id):
        """Fetches user profile details."""
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }), 200
