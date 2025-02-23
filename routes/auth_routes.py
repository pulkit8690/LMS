import random
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta,datetime
from backend.models import User, db, UserOTP
from flask_mail import Message
from backend.app import mail  # Ensure correct mail import

auth_bp = Blueprint("auth", __name__)

# ✅ Function to Send OTP
def send_otp(email, otp):
    """Send OTP to the user's email address."""
    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f"Your OTP code is: {otp}"

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False

# ✅ Signup Route (Step 1: Send OTP)
@auth_bp.route("/signup", methods=["POST"], endpoint="auth_signup")
def signup():
    """Registers a new user and sends OTP for email verification."""
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    # ✅ Generate OTP
    otp = random.randint(100000, 999999)

    # ✅ Store OTP (update if email exists)
    user_otp = UserOTP.query.filter_by(email=email).first()
    if user_otp:
        user_otp.otp = otp
        user_otp.created_at = datetime.utcnow()  # Update timestamp
    else:
        user_otp = UserOTP(email=email, otp=otp)
        db.session.add(user_otp)
    
    db.session.commit()

    # ✅ Send OTP to email
    if not send_otp(email, otp):
        return jsonify({"error": "Error sending OTP"}), 500

    return jsonify({"message": "OTP sent to your email. Verify to complete registration."}), 201


# ✅ OTP Verification Route (Step 2: Verify & Create User)
@auth_bp.route("/verify_otp", methods=["POST"], endpoint="auth_verify_otp")
def verify_otp():
    """Verify OTP and create user in the database."""
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    name = data.get("name")  # Ensure name is passed again
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not otp or not name or not password:
        return jsonify({"error": "All fields are required"}), 400

    # ✅ Check if OTP is valid
    user_otp = UserOTP.query.filter_by(email=email, otp=otp).first()
    if not user_otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # ✅ Check if user already exists (shouldn't happen)
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already registered"}), 400

    # ✅ Create User after OTP verification
    new_user = User(name=name, email=email, role=role, is_verified=True)
    new_user.set_password(password)  # ✅ Hash password properly

    db.session.add(new_user)
    db.session.delete(user_otp)  # ✅ Remove OTP entry after successful verification
    db.session.commit()

    return jsonify({"message": "Email verified and account created successfully."}), 201


# ✅ Login Route (Tracks Failed Attempts)
@auth_bp.route("/login", methods=["POST"], endpoint="auth_login")
def login():
    """Log in the user and send OTP for email verification if too many failed attempts."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Check if password is correct
    if not user.check_password(password):
        user.login_attempts += 1  # ✅ Increment failed attempts
        db.session.commit()

        # ✅ Send OTP if failed login attempts reach 2
        if user.login_attempts >= 2:
            otp = random.randint(100000, 999999)

            # ✅ Store OTP (update if exists)
            user_otp = UserOTP.query.filter_by(email=email).first()
            if user_otp:
                user_otp.otp = otp
                user_otp.created_at = datetime.utcnow()
            else:
                user_otp = UserOTP(email=email, otp=otp)
                db.session.add(user_otp)

            db.session.commit()

            # ✅ Send OTP to email
            if not send_otp(email, otp):
                return jsonify({"error": "Error sending OTP"}), 500

            return jsonify({"message": "Too many failed attempts. OTP sent to your email."}), 403

        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Reset failed attempts after successful login
    user.login_attempts = 0
    db.session.commit()

    # ✅ Generate tokens
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200


# ✅ Verify Login OTP
@auth_bp.route("/verify_login_otp", methods=["POST"], endpoint="auth_verify_login_otp")
def verify_login_otp():
    """Verify OTP during login."""
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    # ✅ Check if OTP is valid
    user_otp = UserOTP.query.filter_by(email=email, otp=otp).first()
    if not user_otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # ✅ Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # ✅ Reset failed attempts & delete OTP after successful login
    user.login_attempts = 0
    db.session.delete(user_otp)
    db.session.commit()

    # ✅ Generate tokens
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200

# ✅ Profile Route
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "name": user.name, "email": user.email, "role": user.role}), 200

@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    """Generate OTP for password reset and send it to the user's email."""
    data = request.json
    email = data.get("email")

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate OTP
    otp = random.randint(100000, 999999)

    # Store OTP (update if email exists)
    user_otp = UserOTP.query.filter_by(email=email).first()
    if user_otp:
        user_otp.otp = otp
        user_otp.created_at = datetime.utcnow()
    else:
        user_otp = UserOTP(email=email, otp=otp)
        db.session.add(user_otp)

    db.session.commit()

    # Send OTP to email
    if not send_otp(email, otp):
        return jsonify({"error": "Error sending OTP"}), 500

    return jsonify({"message": "OTP sent to your email. Please verify to reset password."}), 200


@auth_bp.route("/verify_password_reset_otp", methods=["POST"])
def verify_password_reset_otp():
    """Verify OTP for password reset."""
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    # Check if OTP exists
    user_otp = UserOTP.query.filter_by(email=email, otp=otp).first()
    if not user_otp:
        return jsonify({"error": "Invalid OTP or OTP expired"}), 400

    return jsonify({"message": "OTP verified successfully. You can now reset your password."}), 200


@auth_bp.route("/reset_password", methods=["POST"])
def reset_password():
    """Allow user to reset password after OTP verification."""
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if not new_password or len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    # Check if OTP is valid
    user_otp = UserOTP.query.filter_by(email=email, otp=otp).first()
    if not user_otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # Find the user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password reset successfully. You can now log in."}), 200

