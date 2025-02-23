from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from models import User, db  # ✅ Removed `backend.`
from flask import jsonify

def register_user(name, email, password, role="user"):
    """Registers a new user in the system."""
    if not name or not email or not password:
        return {"error": "All fields are required"}, 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {"error": "Email already exists"}, 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User registered successfully"}, 201

def authenticate_user(email, password):
    """Authenticates a user and generates an access token."""
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(
        identity={"id": user.id, "role": user.role},  # Include "role" inside identity
        expires_delta=timedelta(days=1)
    )
    
    refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role})
    
    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200

def get_user_profile(user_id):
    """Fetches user profile details."""
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }, 200
