# routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from datetime import timedelta, datetime
import random

# Import Flask-Mail for sending OTP emails
from extensions import mail
from models import db
from models.user_model import User, UserOTP
from flask_mail import Message

auth_bp = Blueprint("auth", __name__)

# ✅ Send OTP via Email
def send_otp(email, otp):
    """Send OTP to the user's email address."""
    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f"Your OTP code is: {otp}"

    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending OTP: {e}")
        return False


# ✅ Signup (Step 1: Send OTP)
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    otp = str(random.randint(100000, 999999))  # ✅ Generate a 6-digit OTP as string

    user_otp = UserOTP.query.filter_by(email=email).first()
    if user_otp:
        user_otp.otp = otp  # ✅ Store OTP as plain text
        user_otp.created_at = datetime.utcnow()
    else:
        user_otp = UserOTP(email=email, otp=otp)  # ✅ Store OTP as plain text
        db.session.add(user_otp)

    db.session.commit()

    if not send_otp(email, otp):
        return jsonify({"error": "Error sending OTP"}), 500

    return jsonify({"message": "OTP sent to your email. Verify to complete registration."}), 201


@auth_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email", "").strip()
    otp = str(data.get("otp", "")).strip()
    name = data.get("name", "").strip()
    password = data.get("password", "").strip()

    print(f"🔍 Received OTP Verification Request: Email={email}, OTP={otp}, Name={name}, Password={password}")

    if not email or not otp or not name or not password:
        return jsonify({"error": "All fields are required"}), 400

    user_otp = UserOTP.query.filter_by(email=email).first()
    
    if not user_otp:
        return jsonify({"error": "OTP expired or not found. Request a new OTP."}), 400

    print(f"Stored OTP: {user_otp.otp if user_otp else None}, Received OTP: {otp}")

    if user_otp.otp.strip() != otp:
        return jsonify({"error": "Invalid OTP!"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already registered"}), 400

    new_user = User(name=name, email=email, is_verified=True)

    if not password:
        return jsonify({"error": "Password is required"}), 400

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.delete(user_otp)  # ✅ Delete OTP after verification
    db.session.commit()

    return jsonify({"message": "Email verified and account created successfully."}), 201



# ✅ Login Route with Role-Based Authentication
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user").lower()

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials!"}), 401

    # ✅ Ensure the role matches
    if user.role != role:
        return jsonify({"error": "Unauthorized role selection!"}), 403

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "email": user.email, "role": user.role}
    }), 200


# ✅ User Profile Route
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_verified": user.is_verified
    }), 200


# ✅ Forgot Password Route
@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = str(random.randint(100000, 999999))  # ✅ Generate a new OTP

    user_otp = UserOTP.query.filter_by(email=email).first()
    if user_otp:
        user_otp.otp = otp  # ✅ Store OTP as plaintext
        user_otp.created_at = datetime.utcnow()
    else:
        user_otp = UserOTP(email=email, otp=otp)
        db.session.add(user_otp)

    db.session.commit()

    if not send_otp(email, otp):
        return jsonify({"error": "Error sending OTP"}), 500

    return jsonify({"message": "OTP sent to your email. Please verify to reset password."}), 200


# ✅ Reset Password Route
@auth_bp.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    otp = str(data.get("otp"))
    new_password = data.get("new_password")

    if not new_password or len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    user_otp = UserOTP.query.filter_by(email=email).first()
    if not user_otp:
        return jsonify({"error": "OTP expired or not found"}), 400

    if user_otp.otp != otp:
        return jsonify({"error": "Invalid OTP!"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.set_password(new_password)
    db.session.delete(user_otp)  # ✅ Delete OTP after reset
    db.session.commit()

    return jsonify({"message": "Password reset successfully. You can now log in."}), 200
